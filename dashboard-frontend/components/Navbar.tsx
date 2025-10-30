/**
 * Navbar Component
 */

'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { FiLogOut, FiUser, FiMenu, FiX } from 'react-icons/fi';

interface User {
  id: string;
  username: string;
  discriminator: string;
  avatar: string | null;
}

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  const getAvatarUrl = () => {
    if (user?.avatar) {
      return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`;
    }
    return `https://cdn.discordapp.com/embed/avatars/${parseInt(user?.id || '0') % 5}.png`;
  };

  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center">
              <span className="text-2xl font-bold">Kingdom-77</span>
              <span className="ml-2 text-sm bg-indigo-500 px-2 py-1 rounded">Dashboard</span>
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/dashboard"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname === '/dashboard' ? 'bg-indigo-700' : 'hover:bg-indigo-500'
              }`}
            >
              Dashboard
            </Link>
            <Link
              href="/servers"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                pathname.startsWith('/servers') ? 'bg-indigo-700' : 'hover:bg-indigo-500'
              }`}
            >
              Servers
            </Link>

            {user && (
              <div className="flex items-center space-x-3 ml-4 border-l border-indigo-500 pl-4">
                <img
                  src={getAvatarUrl()}
                  alt={user.username}
                  className="w-8 h-8 rounded-full"
                />
                <span className="text-sm">{user.username}</span>
                <button
                  onClick={handleLogout}
                  className="p-2 hover:bg-indigo-500 rounded-md"
                  title="Logout"
                >
                  <FiLogOut />
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 hover:bg-indigo-500 rounded-md"
            >
              {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link
              href="/dashboard"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                pathname === '/dashboard' ? 'bg-indigo-700' : 'hover:bg-indigo-500'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              href="/servers"
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                pathname.startsWith('/servers') ? 'bg-indigo-700' : 'hover:bg-indigo-500'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Servers
            </Link>
            {user && (
              <button
                onClick={() => {
                  handleLogout();
                  setMobileMenuOpen(false);
                }}
                className="w-full text-left px-3 py-2 rounded-md text-base font-medium hover:bg-indigo-500"
              >
                Logout
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
