"use client";

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

// ============================================================
// TYPES
// ============================================================

interface CreditPackage {
  package_id: string;
  name: string;
  name_ar: string;
  base_credits: number;
  bonus_credits: number;
  total_credits: number;
  price_usd: number;
  price_sar: number;
  popular: boolean;
  emoji: string;
  badge?: string;
}

interface ShopItem {
  item_id: string;
  name: string;
  name_ar: string;
  description: string;
  description_ar: string;
  type: string;
  price: number;
  rarity: string;
  rarity_emoji: string;
  rarity_color: number;
  preview_url?: string;
  color?: string;
  emoji: string;
  total_sales: number;
  owned: boolean;
  equipped: boolean;
}

interface UserBalance {
  user_id: number;
  username: string;
  balance: number;
  total_earned: number;
  total_spent: number;
  total_purchased: number;
  daily_claim_streak: number;
  can_claim_daily: boolean;
  next_claim_time?: string;
}

// ============================================================
// MAIN COMPONENT
// ============================================================

export default function ShopPage() {
  const { user } = useAuth();
  
  const [activeTab, setActiveTab] = useState<'packages' | 'shop'>('packages');
  const [shopCategory, setShopCategory] = useState<'all' | 'frames' | 'badges' | 'banners' | 'themes'>('all');
  
  const [balance, setBalance] = useState<UserBalance | null>(null);
  const [packages, setPackages] = useState<CreditPackage[]>([]);
  const [shopItems, setShopItems] = useState<ShopItem[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState<string | null>(null);
  const [claiming, setClaiming] = useState(false);
  
  const [selectedItem, setSelectedItem] = useState<ShopItem | null>(null);

  // ============================================================
  // FETCH DATA
  // ============================================================

  useEffect(() => {
    if (user) {
      fetchBalance();
      fetchPackages();
      fetchShopItems();
    }
  }, [user]);

  const fetchBalance = async () => {
    try {
      const response = await fetch(`/api/credits/${user?.id}/balance?username=${user?.username}`);
      if (response.ok) {
        const data = await response.json();
        setBalance(data);
      }
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  };

  const fetchPackages = async () => {
    try {
      const response = await fetch('/api/credits/packages');
      if (response.ok) {
        const data = await response.json();
        setPackages(data);
      }
    } catch (error) {
      console.error('Failed to fetch packages:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchShopItems = async () => {
    try {
      const itemType = shopCategory === 'all' ? '' : shopCategory;
      const response = await fetch(`/api/shop/items?item_type=${itemType}&user_id=${user?.id}`);
      if (response.ok) {
        const data = await response.json();
        setShopItems(data);
      }
    } catch (error) {
      console.error('Failed to fetch shop items:', error);
    }
  };

  useEffect(() => {
    if (user && activeTab === 'shop') {
      fetchShopItems();
    }
  }, [shopCategory, user, activeTab]);

  // ============================================================
  // ACTIONS
  // ============================================================

  const handleClaimDaily = async () => {
    if (!user || !balance?.can_claim_daily) return;
    
    setClaiming(true);
    try {
      const response = await fetch(`/api/credits/${user.id}/daily-claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          username: user.username
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${data.message}`);
        fetchBalance();
      } else {
        const error = await response.json();
        alert(`❌ ${error.detail.message || error.detail}`);
      }
    } catch (error) {
      console.error('Failed to claim daily:', error);
      alert('❌ Failed to claim daily credits');
    } finally {
      setClaiming(false);
    }
  };

  const handlePurchasePackage = async (packageId: string) => {
    if (!user) return;
    
    setPurchasing(packageId);
    try {
      const response = await fetch('/api/credits/purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          username: user.username,
          package_id: packageId,
          payment_method: 'moyasar'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Redirect to payment
        window.location.href = data.payment_url;
      } else {
        const error = await response.json();
        alert(`❌ ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to purchase package:', error);
      alert('❌ Failed to create payment');
    } finally {
      setPurchasing(null);
    }
  };

  const handlePurchaseItem = async (item: ShopItem) => {
    if (!user) return;
    
    if (item.owned) {
      alert('You already own this item!');
      return;
    }
    
    if (!balance || balance.balance < item.price) {
      alert(`Insufficient credits! You need ${item.price} ❄️ but have ${balance?.balance || 0} ❄️`);
      return;
    }
    
    const confirmed = confirm(`Purchase ${item.name} for ${item.price} ❄️?`);
    if (!confirmed) return;
    
    setPurchasing(item.item_id);
    try {
      const response = await fetch(`/api/shop/${user.id}/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          username: user.username,
          item_id: item.item_id
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${data.message}`);
        fetchBalance();
        fetchShopItems();
      } else {
        const error = await response.json();
        alert(`❌ ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to purchase item:', error);
      alert('❌ Failed to purchase item');
    } finally {
      setPurchasing(null);
    }
  };

  const handleEquipItem = async (item: ShopItem) => {
    if (!user || !item.owned) return;
    
    setPurchasing(item.item_id);
    try {
      const response = await fetch(`/api/shop/${user.id}/equip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          item_id: item.item_id
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ ${data.message}`);
        fetchShopItems();
      } else {
        const error = await response.json();
        alert(`❌ ${error.detail}`);
      }
    } catch (error) {
      console.error('Failed to equip item:', error);
      alert('❌ Failed to equip item');
    } finally {
      setPurchasing(null);
    }
  };

  // ============================================================
  // RENDER
  // ============================================================

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-400">Please login to access the shop</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold mb-2">❄️ K77 Credits Shop</h1>
        <p className="text-gray-400">Purchase credits and customize your profile</p>
      </div>

      {/* Balance Card */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-gradient-to-r from-blue-900 to-purple-900 rounded-lg p-6 shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 mb-1">Your Balance</p>
              <p className="text-5xl font-bold">{balance?.balance || 0} ❄️</p>
              <p className="text-sm text-gray-400 mt-2">
                Streak: {balance?.daily_claim_streak || 0} days 🔥
              </p>
            </div>
            
            <button
              onClick={handleClaimDaily}
              disabled={!balance?.can_claim_daily || claiming}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                balance?.can_claim_daily
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-gray-700 cursor-not-allowed'
              }`}
            >
              {claiming ? 'Claiming...' : balance?.can_claim_daily ? '🎁 Claim Daily' : '⏳ Claimed Today'}
            </button>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-700">
            <div>
              <p className="text-gray-400 text-sm">Total Earned</p>
              <p className="text-xl font-bold">{balance?.total_earned || 0} ❄️</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Total Spent</p>
              <p className="text-xl font-bold">{balance?.total_spent || 0} ❄️</p>
            </div>
            <div>
              <p className="text-gray-400 text-sm">Total Purchased</p>
              <p className="text-xl font-bold">{balance?.total_purchased || 0} ❄️</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex gap-4 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('packages')}
            className={`px-6 py-3 font-semibold transition ${
              activeTab === 'packages'
                ? 'text-blue-500 border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            💰 Credit Packages
          </button>
          <button
            onClick={() => setActiveTab('shop')}
            className={`px-6 py-3 font-semibold transition ${
              activeTab === 'shop'
                ? 'text-blue-500 border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            🛍️ Item Shop
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {activeTab === 'packages' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {packages.map((pkg) => (
              <div
                key={pkg.package_id}
                className={`bg-gray-800 rounded-lg p-6 border-2 transition hover:scale-105 ${
                  pkg.popular ? 'border-yellow-500' : 'border-gray-700'
                }`}
              >
                {pkg.badge && (
                  <div className="bg-yellow-500 text-black text-xs font-bold px-3 py-1 rounded-full inline-block mb-3">
                    {pkg.badge}
                  </div>
                )}
                
                <div className="text-5xl mb-3">{pkg.emoji}</div>
                <h3 className="text-xl font-bold mb-2">{pkg.name}</h3>
                
                <div className="mb-4">
                  <p className="text-3xl font-bold text-blue-400">
                    {pkg.total_credits} ❄️
                  </p>
                  <p className="text-sm text-gray-400">
                    {pkg.base_credits} + {pkg.bonus_credits} bonus
                  </p>
                </div>
                
                <div className="mb-4">
                  <p className="text-2xl font-bold">${pkg.price_usd}</p>
                  <p className="text-sm text-gray-400">{pkg.price_sar} SAR</p>
                </div>
                
                <button
                  onClick={() => handlePurchasePackage(pkg.package_id)}
                  disabled={purchasing === pkg.package_id}
                  className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-3 rounded-lg font-semibold transition disabled:opacity-50"
                >
                  {purchasing === pkg.package_id ? 'Processing...' : 'Purchase'}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Shop Categories */}
            <div className="flex gap-4 mb-6">
              {['all', 'frames', 'badges', 'banners', 'themes'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setShopCategory(cat as any)}
                  className={`px-4 py-2 rounded-lg font-semibold transition ${
                    shopCategory === cat
                      ? 'bg-blue-600'
                      : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                >
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </button>
              ))}
            </div>

            {/* Shop Items */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {shopItems.map((item) => (
                <div
                  key={item.item_id}
                  className="bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-700 hover:border-gray-600 transition cursor-pointer"
                  onClick={() => setSelectedItem(item)}
                >
                  {/* Preview */}
                  <div 
                    className="h-40 flex items-center justify-center text-6xl"
                    style={{ backgroundColor: item.color || '#1f2937' }}
                  >
                    {item.emoji}
                  </div>
                  
                  {/* Info */}
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-lg">{item.rarity_emoji}</span>
                      {item.owned && (
                        <span className="bg-green-600 text-xs px-2 py-1 rounded">
                          {item.equipped ? '✓ Equipped' : 'Owned'}
                        </span>
                      )}
                    </div>
                    
                    <h3 className="font-bold mb-1">{item.name}</h3>
                    <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                      {item.description}
                    </p>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-blue-400">
                        {item.price} ❄️
                      </span>
                      
                      {item.owned ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEquipItem(item);
                          }}
                          disabled={item.equipped || purchasing === item.item_id}
                          className={`px-3 py-1 rounded text-sm font-semibold transition ${
                            item.equipped
                              ? 'bg-gray-700 cursor-not-allowed'
                              : 'bg-blue-600 hover:bg-blue-700'
                          }`}
                        >
                          {item.equipped ? 'Equipped' : 'Equip'}
                        </button>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePurchaseItem(item);
                          }}
                          disabled={purchasing === item.item_id}
                          className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm font-semibold transition disabled:opacity-50"
                        >
                          {purchasing === item.item_id ? 'Buying...' : 'Buy'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Item Preview Modal */}
      {selectedItem && (
        <div
          className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedItem(null)}
        >
          <div
            className="bg-gray-800 rounded-lg max-w-2xl w-full p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-3xl font-bold mb-2">{selectedItem.name}</h2>
                <p className="text-gray-400">{selectedItem.description}</p>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
            
            <div
              className="h-64 rounded-lg flex items-center justify-center text-9xl mb-6"
              style={{ backgroundColor: selectedItem.color || '#1f2937' }}
            >
              {selectedItem.emoji}
            </div>
            
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-gray-400 text-sm mb-1">Rarity</p>
                <p className="text-xl">
                  {selectedItem.rarity_emoji} {selectedItem.rarity}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Total Sales</p>
                <p className="text-xl">{selectedItem.total_sales}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Price</p>
                <p className="text-2xl font-bold text-blue-400">
                  {selectedItem.price} ❄️
                </p>
              </div>
            </div>
            
            {selectedItem.owned ? (
              <button
                onClick={() => handleEquipItem(selectedItem)}
                disabled={selectedItem.equipped}
                className={`w-full py-3 rounded-lg font-semibold transition ${
                  selectedItem.equipped
                    ? 'bg-gray-700 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {selectedItem.equipped ? '✓ Equipped' : 'Equip Item'}
              </button>
            ) : (
              <button
                onClick={() => handlePurchaseItem(selectedItem)}
                className="w-full bg-green-600 hover:bg-green-700 py-3 rounded-lg font-semibold transition"
              >
                Purchase for {selectedItem.price} ❄️
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
