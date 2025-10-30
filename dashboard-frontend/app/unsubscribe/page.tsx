'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function UnsubscribePage() {
  const searchParams = useSearchParams();
  const userIdFromUrl = searchParams.get('user_id') || '';
  
  const [userId, setUserId] = useState(userIdFromUrl);
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleUnsubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userId.trim()) {
      setError('Please enter your User ID');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      const res = await fetch(`/api/emails/${userId}/unsubscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          reason: reason || 'No reason provided'
        })
      });
      
      if (res.ok) {
        setSuccess(true);
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to unsubscribe. Please try again.');
      }
    } catch (err) {
      console.error('Error unsubscribing:', err);
      setError('An error occurred. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 to-black px-4">
        <div className="max-w-md w-full bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-3xl font-bold mb-4 text-white">Successfully Unsubscribed</h1>
          <p className="text-gray-400 mb-6">
            You have been successfully unsubscribed from all Kingdom-77 email notifications.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            You can resubscribe anytime from your dashboard settings.
          </p>
          <Link
            href="/"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            🏠 Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-gray-900 to-black px-4">
      <div className="max-w-md w-full bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-8">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">📧</div>
          <h1 className="text-3xl font-bold mb-2 text-white">Unsubscribe</h1>
          <p className="text-gray-400">
            We&apos;re sorry to see you go! Unsubscribe from Kingdom-77 email notifications.
          </p>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 mb-6">
            <p className="text-red-400 text-sm">❌ {error}</p>
          </div>
        )}

        <form onSubmit={handleUnsubscribe} className="space-y-6">
          <div>
            <label htmlFor="userId" className="block text-sm font-semibold text-gray-300 mb-2">
              User ID <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              id="userId"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter your Discord User ID"
              className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              You can find your User ID in the emails we sent you
            </p>
          </div>

          <div>
            <label htmlFor="reason" className="block text-sm font-semibold text-gray-300 mb-2">
              Reason (Optional)
            </label>
            <textarea
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Tell us why you're unsubscribing (optional)"
              rows={4}
              className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Processing...' : '🚫 Unsubscribe from All Emails'}
          </button>

          <p className="text-xs text-gray-500 text-center">
            By unsubscribing, you will stop receiving all email notifications from Kingdom-77.
            You can resubscribe anytime from your dashboard settings.
          </p>
        </form>
      </div>
    </div>
  );
}
