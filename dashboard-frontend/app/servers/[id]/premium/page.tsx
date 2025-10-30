/**
 * Premium Management Page
 * Manage premium subscription for the server
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams, useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Loading from '@/components/Loading';
import { 
  FiCheck, FiX, FiCreditCard, FiPackage, FiZap, FiStar,
  FiShield, FiTrendingUp, FiSettings, FiExternalLink 
} from 'react-icons/fi';

interface Subscription {
  guild_id: string;
  tier: 'basic' | 'premium';
  status: string;
  start_date?: string;
  end_date?: string;
  auto_renew: boolean;
  trial_used: boolean;
  features: string[];
}

interface Feature {
  name: string;
  display_name: string;
  description: string;
  enabled: boolean;
  premium_only: boolean;
}

interface BillingHistoryItem {
  invoice_id: string;
  amount: number;
  currency: string;
  status: string;
  date: string;
  description: string;
  invoice_url?: string;
}

export default function PremiumPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const guildId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [features, setFeatures] = useState<{ basic: Feature[]; premium: Feature[] } | null>(null);
  const [billingHistory, setBillingHistory] = useState<BillingHistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showBilling, setShowBilling] = useState(false);
  const [processingAction, setProcessingAction] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/');
        return;
      }

      try {
        // Fetch subscription
        const subResponse = await fetch(`http://localhost:8000/api/premium/${guildId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const subData = await subResponse.json();
        if (subData.success) {
          setSubscription(subData.data);
        }

        // Fetch features
        const featuresResponse = await fetch(`http://localhost:8000/api/premium/${guildId}/features`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const featuresData = await featuresResponse.json();
        if (featuresData.success) {
          setFeatures(featuresData.data.features);
        }

        // Fetch billing history
        const billingResponse = await fetch(`http://localhost:8000/api/premium/${guildId}/billing`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const billingData = await billingResponse.json();
        if (billingData.success) {
          setBillingHistory(billingData.data.billing_history);
        }

      } catch (err: any) {
        console.error('Failed to fetch premium data:', err);
        setError('Failed to load premium information');
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Check for success/cancel from Stripe
    if (searchParams.get('success') === 'true') {
      setError(null);
      // Show success message
      setTimeout(() => {
        window.location.href = `/servers/${guildId}/premium`;
      }, 2000);
    } else if (searchParams.get('canceled') === 'true') {
      setError('Payment was canceled');
    }
  }, [guildId, router, searchParams]);

  const handleSubscribe = async (billingCycle: 'monthly' | 'yearly') => {
    const token = localStorage.getItem('token');
    if (!token) return;

    setProcessingAction(true);
    try {
      const response = await fetch(`http://localhost:8000/api/premium/${guildId}/subscribe`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tier: 'premium',
          billing_cycle: billingCycle
        })
      });

      const data = await response.json();
      if (data.success) {
        // Redirect to Stripe checkout
        window.location.href = data.data.checkout_url;
      } else {
        setError(data.message || 'Failed to create checkout session');
      }
    } catch (err) {
      setError('Failed to process subscription');
    } finally {
      setProcessingAction(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will keep access until the end of the billing period.')) {
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) return;

    setProcessingAction(true);
    try {
      const response = await fetch(`http://localhost:8000/api/premium/${guildId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (data.success) {
        alert('Subscription cancelled. You will keep access until ' + new Date(data.data.end_date).toLocaleDateString());
        window.location.reload();
      } else {
        setError(data.message || 'Failed to cancel subscription');
      }
    } catch (err) {
      setError('Failed to cancel subscription');
    } finally {
      setProcessingAction(false);
    }
  };

  const handleManageBilling = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    setProcessingAction(true);
    try {
      const response = await fetch(`http://localhost:8000/api/premium/${guildId}/portal`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (data.success) {
        // Redirect to Stripe Customer Portal
        window.location.href = data.data.portal_url;
      } else {
        setError(data.message || 'Failed to open billing portal');
      }
    } catch (err) {
      setError('Failed to open billing portal');
    } finally {
      setProcessingAction(false);
    }
  };

  if (loading) {
    return <Loading />;
  }

  const isPremium = subscription?.tier === 'premium' && subscription?.status === 'active';

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <FiStar className="text-yellow-500" />
            Premium Subscription
          </h1>
          <p className="text-gray-600 mt-2">
            Unlock powerful features for your server
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {searchParams.get('success') === 'true' && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
            ✅ Payment successful! Your premium features are now active.
          </div>
        )}

        {/* Current Subscription Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <FiPackage />
              Current Plan
            </h2>
            {isPremium && (
              <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-full font-semibold text-sm">
                💎 Premium Active
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Tier</p>
              <p className="text-lg font-semibold capitalize">
                {subscription?.tier || 'Basic'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="text-lg font-semibold capitalize">
                {subscription?.status || 'Active'}
              </p>
            </div>
            {subscription?.end_date && (
              <div>
                <p className="text-sm text-gray-600">Renewal Date</p>
                <p className="text-lg font-semibold">
                  {new Date(subscription.end_date).toLocaleDateString()}
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex gap-4">
            {!isPremium ? (
              <>
                <button
                  onClick={() => handleSubscribe('monthly')}
                  disabled={processingAction}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
                >
                  <FiZap />
                  Upgrade to Premium - $9.99/mo
                </button>
                <button
                  onClick={() => handleSubscribe('yearly')}
                  disabled={processingAction}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
                >
                  <FiStar />
                  Upgrade to Premium - $99.99/yr
                  <span className="text-xs bg-white text-purple-600 px-2 py-1 rounded">Save 17%</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleManageBilling}
                  disabled={processingAction}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <FiCreditCard />
                  Manage Billing
                </button>
                <button
                  onClick={handleCancel}
                  disabled={processingAction}
                  className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <FiX />
                  Cancel Subscription
                </button>
              </>
            )}
          </div>
        </div>

        {/* Features Comparison */}
        {features && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <FiSettings />
              Features
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Features */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">🆓 Basic Features</h3>
                <div className="space-y-3">
                  {features.basic.map((feature) => (
                    <div key={feature.name} className="flex items-start gap-3">
                      <FiCheck className="text-green-500 mt-1 flex-shrink-0" />
                      <div>
                        <p className="font-medium text-gray-900">{feature.display_name}</p>
                        <p className="text-sm text-gray-600">{feature.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Premium Features */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  💎 Premium Features
                  {!isPremium && <span className="text-xs bg-purple-100 text-purple-600 px-2 py-1 rounded">Upgrade Required</span>}
                </h3>
                <div className="space-y-3">
                  {features.premium.map((feature) => (
                    <div 
                      key={feature.name} 
                      className={`flex items-start gap-3 ${!feature.enabled ? 'opacity-50' : ''}`}
                    >
                      {feature.enabled ? (
                        <FiCheck className="text-green-500 mt-1 flex-shrink-0" />
                      ) : (
                        <FiX className="text-gray-400 mt-1 flex-shrink-0" />
                      )}
                      <div>
                        <p className="font-medium text-gray-900">{feature.display_name}</p>
                        <p className="text-sm text-gray-600">{feature.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Billing History */}
        {isPremium && billingHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <FiTrendingUp />
                Billing History
              </h2>
              <button
                onClick={() => setShowBilling(!showBilling)}
                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
              >
                {showBilling ? 'Hide' : 'Show'} Details
              </button>
            </div>

            {showBilling && (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Description</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Amount</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Invoice</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {billingHistory.map((item) => (
                      <tr key={item.invoice_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {new Date(item.date).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">{item.description}</td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          ${item.amount.toFixed(2)} {item.currency.toUpperCase()}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${
                            item.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {item.invoice_url && (
                            <a
                              href={item.invoice_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-700 flex items-center gap-1"
                            >
                              View
                              <FiExternalLink size={14} />
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Premium Benefits Banner */}
        {!isPremium && (
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg shadow-lg p-8 text-white mt-8">
            <h2 className="text-2xl font-bold mb-4">🚀 Upgrade to Premium Today!</h2>
            <p className="text-lg mb-6">
              Unlock advanced features, 2x XP boost, custom level cards, and much more!
            </p>
            <ul className="space-y-2 mb-6">
              <li className="flex items-center gap-2">
                <FiCheck />
                <span>Cancel anytime, no long-term commitment</span>
              </li>
              <li className="flex items-center gap-2">
                <FiCheck />
                <span>Full access to all premium features instantly</span>
              </li>
              <li className="flex items-center gap-2">
                <FiCheck />
                <span>Priority support from our team</span>
              </li>
            </ul>
            <button
              onClick={() => handleSubscribe('monthly')}
              disabled={processingAction}
              className="bg-white text-purple-600 px-8 py-3 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              Get Started Now
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
