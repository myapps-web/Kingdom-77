/**
 * Dashboard Page - Main dashboard with overview
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Loading from '@/components/Loading';
import { FiServer, FiUsers, FiActivity, FiShield } from 'react-icons/fi';

export default function Dashboard() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/');
      return;
    }

    if (userData) {
      setUser(JSON.parse(userData));
    }

    setLoading(false);
  }, [router]);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-600">
            Manage your Discord servers and bot settings from here.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Your Servers"
            value="0"
            icon={<FiServer size={24} />}
            color="bg-indigo-100 text-indigo-600"
          />
          <StatCard
            title="Total Members"
            value="0"
            icon={<FiUsers size={24} />}
            color="bg-green-100 text-green-600"
          />
          <StatCard
            title="Commands Used"
            value="0"
            icon={<FiActivity size={24} />}
            color="bg-blue-100 text-blue-600"
          />
          <StatCard
            title="Mod Actions"
            value="0"
            icon={<FiShield size={24} />}
            color="bg-purple-100 text-purple-600"
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <ActionButton
              href="/servers"
              title="View Servers"
              description="Manage your servers"
            />
            <ActionButton
              href="https://discord.com/developers/applications"
              title="Discord Developer Portal"
              description="Manage your bot application"
              external
            />
            <ActionButton
              href={`https://discord.com/api/oauth2/authorize?client_id=${process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID}&permissions=8&scope=bot%20applications.commands`}
              title="Add Bot to Server"
              description="Invite bot to a new server"
              external
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function ActionButton({ href, title, description, external = false }: any) {
  const content = (
    <div className="border border-gray-200 rounded-lg p-4 hover:border-indigo-500 hover:shadow-md transition-all cursor-pointer">
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );

  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {content}
      </a>
    );
  }

  return <a href={href}>{content}</a>;
}
