'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface CardDesign {
  guild_id: string;
  template: string;
  background_color: string;
  background_image?: string;
  progress_bar_color: string;
  progress_bar_bg_color: string;
  text_color: string;
  accent_color: string;
  font: string;
  avatar_border_color: string;
  avatar_border_width: number;
  show_rank: boolean;
  show_progress_percentage: boolean;
}

interface Template {
  id: string;
  name: string;
  description: string;
  background_color: string;
  progress_bar_color: string;
  progress_bar_bg_color: string;
  text_color: string;
  accent_color: string;
  avatar_border_color: string;
}

export default function LevelCardsPage() {
  const params = useParams();
  const guildId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [design, setDesign] = useState<CardDesign | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'templates' | 'customize'>('templates');
  const [isPremium, setIsPremium] = useState(false);

  useEffect(() => {
    fetchData();
  }, [guildId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch current design
      const designRes = await fetch(`/api/leveling/${guildId}/card-design`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (designRes.ok) {
        const designData = await designRes.json();
        setDesign(designData);
      }
      
      // Fetch templates
      const templatesRes = await fetch(`/api/leveling/${guildId}/templates`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (templatesRes.ok) {
        const templatesData = await templatesRes.json();
        setTemplates(templatesData);
      }
      
      // Check premium status
      const premiumRes = await fetch(`/api/premium/${guildId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (premiumRes.ok) {
        const premiumData = await premiumRes.json();
        setIsPremium(premiumData.tier === 'premium');
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = async (templateId: string) => {
    try {
      setSaving(true);
      
      const res = await fetch(`/api/leveling/${guildId}/card-design`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ template: templateId })
      });
      
      if (res.ok) {
        const newDesign = await res.json();
        setDesign(newDesign);
        generatePreview(newDesign);
        alert('✅ Template applied successfully!');
      } else {
        alert('❌ Failed to apply template');
      }
    } catch (error) {
      console.error('Error applying template:', error);
      alert('❌ Error applying template');
    } finally {
      setSaving(false);
    }
  };

  const saveCustomDesign = async () => {
    if (!isPremium) {
      alert('💎 Custom design is a Premium feature!');
      return;
    }
    
    try {
      setSaving(true);
      
      const res = await fetch(`/api/leveling/${guildId}/card-design`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(design)
      });
      
      if (res.ok) {
        const newDesign = await res.json();
        setDesign(newDesign);
        generatePreview(newDesign);
        alert('✅ Design saved successfully!');
      } else {
        alert('❌ Failed to save design');
      }
    } catch (error) {
      console.error('Error saving design:', error);
      alert('❌ Error saving design');
    } finally {
      setSaving(false);
    }
  };

  const generatePreview = async (designData: CardDesign) => {
    try {
      const res = await fetch(`/api/leveling/${guildId}/preview-card`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(designData)
      });
      
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
    }
  };

  const resetDesign = async () => {
    if (!confirm('Are you sure you want to reset to default design?')) {
      return;
    }
    
    try {
      setSaving(true);
      
      const res = await fetch(`/api/leveling/${guildId}/card-design`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (res.ok) {
        await fetchData();
        alert('✅ Reset to default design!');
      } else {
        alert('❌ Failed to reset design');
      }
    } catch (error) {
      console.error('Error resetting design:', error);
      alert('❌ Error resetting design');
    } finally {
      setSaving(false);
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
          🎨 Level Card Designer
        </h1>
        <p className="text-gray-400">
          Customize how level up cards look in your server
        </p>
      </div>

      {/* Premium Banner */}
      {!isPremium && (
        <div className="bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/50 rounded-lg p-6 mb-6">
          <div className="flex items-start">
            <div className="text-4xl mr-4">💎</div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-yellow-400 mb-2">
                Unlock Full Customization with Premium
              </h3>
              <p className="text-gray-300 mb-3">
                Templates are free for everyone, but custom colors, backgrounds, and advanced options require Premium!
              </p>
              <a 
                href={`/servers/${guildId}/premium`}
                className="inline-block bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-2 rounded-lg font-semibold hover:opacity-90 transition-opacity"
              >
                Upgrade to Premium
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('templates')}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === 'templates'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          📋 Templates
        </button>
        <button
          onClick={() => setActiveTab('customize')}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === 'customize'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          🎨 Custom Design {!isPremium && '💎'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Templates or Customization */}
        <div className="lg:col-span-2">
          {activeTab === 'templates' ? (
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-white">Available Templates</h2>
              <p className="text-gray-400 mb-6">Click on a template to apply it instantly</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    onClick={() => applyTemplate(template.id)}
                    className={`bg-gray-700/50 border-2 rounded-lg p-4 cursor-pointer transition-all hover:scale-105 ${
                      design?.template === template.id
                        ? 'border-blue-500'
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-bold text-white">{template.name}</h3>
                      {design?.template === template.id && (
                        <span className="text-green-400 text-sm">✓ Active</span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-400 mb-3">{template.description}</p>
                    
                    {/* Color Preview */}
                    <div className="flex space-x-2 mb-2">
                      <div
                        className="w-12 h-12 rounded border border-gray-600"
                        style={{ backgroundColor: template.background_color }}
                        title="Background"
                      />
                      <div
                        className="w-12 h-12 rounded border border-gray-600"
                        style={{ backgroundColor: template.progress_bar_color }}
                        title="Progress Bar"
                      />
                      <div
                        className="w-12 h-12 rounded border border-gray-600"
                        style={{ backgroundColor: template.accent_color }}
                        title="Accent"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-white">
                Custom Design {!isPremium && '💎'}
              </h2>
              
              {!isPremium ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🔒</div>
                  <p className="text-gray-400 mb-4">
                    Custom design options require Premium
                  </p>
                  <a
                    href={`/servers/${guildId}/premium`}
                    className="inline-block bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity"
                  >
                    Upgrade to Premium
                  </a>
                </div>
              ) : design ? (
                <div className="space-y-4">
                  {/* Background Color */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Background Color
                    </label>
                    <input
                      type="color"
                      value={design.background_color}
                      onChange={(e) => setDesign({ ...design, background_color: e.target.value })}
                      className="w-full h-12 rounded cursor-pointer"
                    />
                  </div>

                  {/* Progress Bar Color */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Progress Bar Color
                    </label>
                    <input
                      type="color"
                      value={design.progress_bar_color}
                      onChange={(e) => setDesign({ ...design, progress_bar_color: e.target.value })}
                      className="w-full h-12 rounded cursor-pointer"
                    />
                  </div>

                  {/* Progress Bar Background */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Progress Bar Background
                    </label>
                    <input
                      type="color"
                      value={design.progress_bar_bg_color}
                      onChange={(e) => setDesign({ ...design, progress_bar_bg_color: e.target.value })}
                      className="w-full h-12 rounded cursor-pointer"
                    />
                  </div>

                  {/* Text Color */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Text Color
                    </label>
                    <input
                      type="color"
                      value={design.text_color}
                      onChange={(e) => setDesign({ ...design, text_color: e.target.value })}
                      className="w-full h-12 rounded cursor-pointer"
                    />
                  </div>

                  {/* Accent Color */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Accent Color
                    </label>
                    <input
                      type="color"
                      value={design.accent_color}
                      onChange={(e) => setDesign({ ...design, accent_color: e.target.value })}
                      className="w-full h-12 rounded cursor-pointer"
                    />
                  </div>

                  {/* Avatar Border */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Avatar Border Color
                    </label>
                    <input
                      type="color"
                      value={design.avatar_border_color}
                      onChange={(e) => setDesign({ ...design, avatar_border_color: e.target.value })}
                      className="w-full h-12 rounded cursor-pointer"
                    />
                  </div>

                  {/* Avatar Border Width */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Avatar Border Width: {design.avatar_border_width}px
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="15"
                      value={design.avatar_border_width}
                      onChange={(e) => setDesign({ ...design, avatar_border_width: parseInt(e.target.value) })}
                      className="w-full"
                    />
                  </div>

                  {/* Show Rank */}
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={design.show_rank}
                      onChange={(e) => setDesign({ ...design, show_rank: e.target.checked })}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label className="ml-2 text-sm text-gray-300">Show Rank</label>
                  </div>

                  {/* Show Progress Percentage */}
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={design.show_progress_percentage}
                      onChange={(e) => setDesign({ ...design, show_progress_percentage: e.target.checked })}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label className="ml-2 text-sm text-gray-300">Show Progress Percentage</label>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-3 pt-4">
                    <button
                      onClick={saveCustomDesign}
                      disabled={saving}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {saving ? 'Saving...' : '💾 Save Design'}
                    </button>
                    <button
                      onClick={() => generatePreview(design)}
                      disabled={saving}
                      className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      🔄 Preview
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>

        {/* Right Panel - Preview */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-lg p-6 sticky top-4">
            <h2 className="text-xl font-bold mb-4 text-white">Preview</h2>
            
            {previewUrl ? (
              <div className="space-y-4">
                <img
                  src={previewUrl}
                  alt="Card Preview"
                  className="w-full rounded-lg border border-gray-600"
                />
                <button
                  onClick={() => generatePreview(design!)}
                  className="w-full bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                >
                  🔄 Refresh Preview
                </button>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-4xl mb-2">🖼️</div>
                <p>Preview will appear here</p>
                {design && (
                  <button
                    onClick={() => generatePreview(design)}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    Generate Preview
                  </button>
                )}
              </div>
            )}

            {/* Current Template Info */}
            {design && (
              <div className="mt-6 p-4 bg-gray-700/50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-300 mb-2">Current Template:</h3>
                <p className="text-white font-bold">
                  {templates.find(t => t.id === design.template)?.name || 'Custom'}
                </p>
              </div>
            )}

            {/* Reset Button */}
            <button
              onClick={resetDesign}
              disabled={saving}
              className="w-full mt-4 bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-600/50 font-semibold py-2 px-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              🔄 Reset to Default
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
