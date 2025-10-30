/**
 * Servers List Page
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import ServerCard from '@/components/ServerCard';
import Loading from '@/components/Loading';
import { servers } from '@/lib/api';

interface Server {
  id: string;
  name: string;
  icon: string | null;
  owner: boolean;
  permissions: number;
  features: string[];
  _has_bot: boolean;
}

export default function ServersPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [serversList, setServersList] = useState<Server[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchServers = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/');
        return;
      }

      try {
        const response = await servers.list();
        setServersList(response.data);
      } catch (err: any) {
        console.error('Failed to fetch servers:', err);
        setError(err.response?.data?.message || 'Failed to load servers');
      } finally {
        setLoading(false);
      }
    };

    fetchServers();
  }, [router]);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Your Servers</h1>
          <p className="text-gray-600 mt-2">
            Manage servers where you have admin permissions
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {serversList.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-600 text-lg mb-4">
              No servers found where you have admin permissions.
            </p>
            <a
              href={`https://discord.com/api/oauth2/authorize?client_id=${process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID}&permissions=8&scope=bot%20applications.commands`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Add Bot to a Server
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {serversList.map((server) => (
              <ServerCard
                key={server.id}
                id={server.id}
                name={server.name}
                icon={server.icon}
                hasBot={server._has_bot}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
