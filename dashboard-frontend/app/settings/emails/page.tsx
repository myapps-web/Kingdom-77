'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface EmailPreferences {
  user_id: string;
  enabled: boolean;
  subscription_emails: boolean;
  payment_emails: boolean;
  trial_emails: boolean;
  weekly_summary: boolean;
  marketing_emails: boolean;
  unsubscribed_at: string | null;
}

interface EmailHistory {
  subject: string;
  type: string;
  status: string;
  sent_at: string;
}

export default function EmailPreferencesPage() {
  const params = useParams();
  const userId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [preferences, setPreferences] = useState<EmailPreferences | null>(null);
  const [emailHistory, setEmailHistory] = useState<EmailHistory[]>([]);
  const [activeTab, setActiveTab] = useState<'preferences' | 'history'>('preferences');

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      
      const res = await fetch(`/api/emails/${userId}/preferences`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setPreferences(data);
      }
    } catch (error) {
      console.error('Error fetching preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`/api/emails/${userId}/history?limit=50`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (res.ok) {
        const data = await res.json();
        setEmailHistory(data.emails || []);
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  useEffect(() => {
    fetchPreferences();
    fetchHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const savePreferences = async () => {
    try {
      setSaving(true);
      
      const res = await fetch(`/api/emails/${userId}/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(preferences)
      });
      
      if (res.ok) {
        alert('✅ Preferences saved successfully!');
        await fetchPreferences();
      } else {
        alert('❌ Failed to save preferences');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('❌ Error saving preferences');
    } finally {
      setSaving(false);
    }
  };

  const unsubscribeAll = async () => {
    if (!confirm('Are you sure you want to unsubscribe from ALL email notifications?')) {
      return;
    }
    
    try {
      setSaving(true);
      
      const res = await fetch(`/api/emails/${userId}/unsubscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          reason: 'User requested from dashboard'
        })
      });
      
      if (res.ok) {
        alert('✅ You have been unsubscribed from all emails');
        await fetchPreferences();
      } else {
        alert('❌ Failed to unsubscribe');
      }
    } catch (error) {
      console.error('Error unsubscribing:', error);
      alert('❌ Error unsubscribing');
    } finally {
      setSaving(false);
    }
  };

  const resubscribe = async () => {
    try {
      setSaving(true);
      
      const res = await fetch(`/api/emails/${userId}/resubscribe`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (res.ok) {
        alert('✅ You have been resubscribed to emails!');
        await fetchPreferences();
      } else {
        alert('❌ Failed to resubscribe');
      }
    } catch (error) {
      console.error('Error resubscribing:', error);
      alert('❌ Error resubscribing');
    } finally {
      setSaving(false);
    }
  };

  const updatePreference = (key: keyof EmailPreferences, value: boolean) => {
    if (preferences) {
      setPreferences({
        ...preferences,
        [key]: value
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          📧 Email Notifications
        </h1>
        <p className="text-gray-400">
          Manage your email notification preferences
        </p>
      </div>

      {/* Unsubscribed Banner */}
      {preferences && !preferences.enabled && (
        <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-6 mb-6">
          <div className="flex items-start">
            <div className="text-4xl mr-4">⚠️</div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-yellow-400 mb-2">
                You are unsubscribed from all emails
              </h3>
              <p className="text-gray-300 mb-3">
                You will not receive any email notifications. Resubscribe to stay updated!
              </p>
              <button
                onClick={resubscribe}
                disabled={saving}
                className="bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {saving ? 'Processing...' : '🔔 Resubscribe'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('preferences')}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === 'preferences'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          ⚙️ Preferences
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === 'history'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          📜 History
        </button>
      </div>

      {activeTab === 'preferences' ? (
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Email Preferences</h2>

          {preferences && (
            <div className="space-y-4">
              {/* Master Toggle */}
              <div className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                <div>
                  <h3 className="text-lg font-bold text-white">Enable All Emails</h3>
                  <p className="text-sm text-gray-400">Master toggle for all email notifications</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={preferences.enabled}
                    onChange={(e) => updatePreference('enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-14 h-7 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              {/* Individual Preferences */}
              <div className="space-y-3">
                <PreferenceToggle
                  title="💎 Subscription Emails"
                  description="New subscriptions, renewals, and cancellations"
                  checked={preferences.subscription_emails}
                  onChange={(checked) => updatePreference('subscription_emails', checked)}
                  disabled={!preferences.enabled}
                />

                <PreferenceToggle
                  title="💳 Payment Emails"
                  description="Payment confirmations and failed payment alerts"
                  checked={preferences.payment_emails}
                  onChange={(checked) => updatePreference('payment_emails', checked)}
                  disabled={!preferences.enabled}
                />

                <PreferenceToggle
                  title="🎉 Trial Emails"
                  description="Trial start and ending reminders"
                  checked={preferences.trial_emails}
                  onChange={(checked) => updatePreference('trial_emails', checked)}
                  disabled={!preferences.enabled}
                />

                <PreferenceToggle
                  title="📊 Weekly Summary"
                  description="Weekly server statistics and reports"
                  checked={preferences.weekly_summary}
                  onChange={(checked) => updatePreference('weekly_summary', checked)}
                  disabled={!preferences.enabled}
                />

                <PreferenceToggle
                  title="📢 Marketing Emails"
                  description="New features, updates, and promotions"
                  checked={preferences.marketing_emails}
                  onChange={(checked) => updatePreference('marketing_emails', checked)}
                  disabled={!preferences.enabled}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4 pt-6">
                <button
                  onClick={savePreferences}
                  disabled={saving}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {saving ? 'Saving...' : '💾 Save Preferences'}
                </button>

                {preferences.enabled && (
                  <button
                    onClick={unsubscribeAll}
                    disabled={saving}
                    className="bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-600/50 font-semibold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    🚫 Unsubscribe All
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-6 text-white">Email History</h2>

          {emailHistory.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-6xl mb-4">📭</div>
              <p>No emails sent yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {emailHistory.map((email, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg hover:bg-gray-700/70 transition-colors"
                >
                  <div className="flex-1">
                    <h3 className="text-white font-semibold">{email.subject}</h3>
                    <p className="text-sm text-gray-400">
                      {email.type} • {new Date(email.sent_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      email.status === 'sent'
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}
                  >
                    {email.status === 'sent' ? '✓ Sent' : '✗ Failed'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function PreferenceToggle({
  title,
  description,
  checked,
  onChange,
  disabled
}: {
  title: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled: boolean;
}) {
  return (
    <div className={`flex items-center justify-between p-4 bg-gray-700/30 rounded-lg ${disabled ? 'opacity-50' : ''}`}>
      <div>
        <h3 className="text-white font-semibold">{title}</h3>
        <p className="text-sm text-gray-400">{description}</p>
      </div>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only peer"
        />
        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
      </label>
    </div>
  );
}
