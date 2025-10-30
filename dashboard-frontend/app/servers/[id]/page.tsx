/**
 * Server Management Page
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Loading from '@/components/Loading';
import StatCard from '@/components/StatCard';
import { stats } from '@/lib/api';
import { formatNumber } from '@/lib/utils';
import { FiUsers, FiActivity, FiShield, FiLifeBuoy, FiAward } from 'react-icons/fi';

export default function ServerDashboard() {
  const router = useRouter();
  const params = useParams();
  const guildId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/');
        return;
      }

      try {
        const response = await stats.overview(guildId);
        setOverview(response.data);
      } catch (err: any) {
        console.error('Failed to fetch stats:', err);
        setError(err.response?.data?.message || 'Failed to load server data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [guildId, router]);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Server Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Overview and statistics for this server
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Leveling Users"
            value={formatNumber(overview?.leveling_users || 0)}
            icon={<FiAward size={24} />}
            color="indigo"
          />
          <StatCard
            title="Active Tickets"
            value={formatNumber(overview?.active_tickets || 0)}
            icon={<FiLifeBuoy size={24} />}
            color="blue"
          />
          <StatCard
            title="Mod Actions (30d)"
            value={formatNumber(overview?.moderation_actions || 0)}
            icon={<FiShield size={24} />}
            color="purple"
          />
          <StatCard
            title="Commands Used"
            value={formatNumber(overview?.total_commands || 0)}
            icon={<FiActivity size={24} />}
            color="green"
          />
        </div>

        {/* Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavCard
            href={`/servers/${guildId}/premium`}
            title="💎 Premium"
            description="Upgrade to unlock advanced features"
            isPremium={true}
          />
          <NavCard
            href={`/servers/${guildId}/leveling`}
            title="Leveling"
            description="View leaderboard and manage role rewards"
          />
          <NavCard
            href={`/servers/${guildId}/level-cards`}
            title="🎨 Level Cards"
            description="Customize level up card designs"
          />
          <NavCard
            href={`/servers/${guildId}/moderation`}
            title="Moderation"
            description="View logs and manage warnings"
          />
          <NavCard
            href={`/servers/${guildId}/tickets`}
            title="Tickets"
            description="Manage open and closed tickets"
          />
          <NavCard
            href={`/servers/${guildId}/settings`}
            title="Settings"
            description="Configure bot settings"
          />
          <NavCard
            href={`/servers/${guildId}/stats`}
            title="Statistics"
            description="Detailed analytics and charts"
          />
        </div>
      </div>
    </div>
  );
}

function NavCard({ href, title, description, isPremium = false }: { href: string; title: string; description: string; isPremium?: boolean }) {
  return (
    <a
      href={href}
      className={`block rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow ${
        isPremium 
          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
          : 'bg-white'
      }`}
    >
      <h3 className={`text-xl font-semibold mb-2 ${isPremium ? 'text-white' : 'text-gray-900'}`}>
        {title}
      </h3>
      <p className={isPremium ? 'text-white/90' : 'text-gray-600'}>
        {description}
      </p>
    </a>
  );
}
