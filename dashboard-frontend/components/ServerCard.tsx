/**
 * Server Card Component
 */

'use client';

import Link from 'next/link';
import { FiServer, FiSettings, FiUsers } from 'react-icons/fi';

interface ServerCardProps {
  id: string;
  name: string;
  icon: string | null;
  hasBot: boolean;
}

export default function ServerCard({ id, name, icon, hasBot }: ServerCardProps) {
  const iconUrl = icon
    ? `https://cdn.discordapp.com/icons/${id}/${icon}.png`
    : null;

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6">
      <div className="flex items-center space-x-4 mb-4">
        {iconUrl ? (
          <img src={iconUrl} alt={name} className="w-16 h-16 rounded-full" />
        ) : (
          <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center">
            <FiServer className="text-indigo-600 text-3xl" />
          </div>
        )}
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900">{name}</h3>
          {hasBot ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Bot Active
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              Bot Not Added
            </span>
          )}
        </div>
      </div>

      <div className="flex space-x-2">
        {hasBot ? (
          <>
            <Link
              href={`/servers/${id}`}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium text-center transition-colors"
            >
              Manage
            </Link>
            <Link
              href={`/servers/${id}/settings`}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
              title="Settings"
            >
              <FiSettings />
            </Link>
          </>
        ) : (
          <a
            href={`https://discord.com/api/oauth2/authorize?client_id=${process.env.NEXT_PUBLIC_DISCORD_CLIENT_ID}&permissions=8&scope=bot%20applications.commands&guild_id=${id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium text-center transition-colors"
          >
            Add Bot
          </a>
        )}
      </div>
    </div>
  );
}
