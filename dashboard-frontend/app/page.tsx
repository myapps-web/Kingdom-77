/**
 * Landing Page - Kingdom-77 Dashboard
 */

'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { FiServer, FiActivity, FiShield, FiAward, FiLifeBuoy } from 'react-icons/fi';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/dashboard');
    }
  }, [router]);

  const handleLogin = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login-url`);
      const data = await response.json();
      if (data.data?.url) {
        window.location.href = data.data.url;
      }
    } catch (error) {
      console.error('Failed to get login URL:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            Kingdom-77
          </h1>
          <p className="text-xl md:text-2xl text-gray-200 mb-8">
            Complete Discord Bot Management Dashboard
          </p>
          <button
            onClick={handleLogin}
            className="bg-white text-indigo-600 hover:bg-gray-100 px-8 py-4 rounded-lg text-lg font-semibold transition-colors shadow-lg"
          >
            Login with Discord
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
          Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <FeatureCard
            icon={<FiServer size={32} />}
            title="Server Management"
            description="Manage all your servers in one place with real-time statistics"
          />
          <FeatureCard
            icon={<FiShield size={32} />}
            title="Moderation System"
            description="Complete moderation tools with warnings, kicks, bans, and more"
          />
          <FeatureCard
            icon={<FiAward size={32} />}
            title="Leveling System"
            description="Nova-style leveling with XP tracking and role rewards"
          />
          <FeatureCard
            icon={<FiLifeBuoy size={32} />}
            title="Ticket System"
            description="Advanced ticket system with priorities and categories"
          />
          <FeatureCard
            icon={<FiActivity size={32} />}
            title="Statistics & Analytics"
            description="Detailed insights into server activity and bot usage"
          />
          <FeatureCard
            icon={<FiServer size={32} />}
            title="Auto-Roles"
            description="Automated role assignment with multiple triggers"
          />
        </div>
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center">
        <p className="text-gray-300">
          Kingdom-77 Bot v3.6 • Built with ❤️ using FastAPI & Next.js
        </p>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 text-white">
      <div className="mb-4 text-indigo-300">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-200">{description}</p>
    </div>
  );
}
