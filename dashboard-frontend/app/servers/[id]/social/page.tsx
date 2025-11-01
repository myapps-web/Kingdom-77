"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { 
  Plus, 
  Edit, 
  Trash2, 
  Power, 
  ShoppingCart,
  Youtube,
  Twitch,
  Twitter,
  Instagram,
  Music,
  Camera,
  ExternalLink,
  TrendingUp
} from "lucide-react";

const PLATFORMS = [
  { id: "youtube", name: "YouTube", icon: Youtube, color: "text-red-600" },
  { id: "twitch", name: "Twitch", icon: Twitch, color: "text-purple-600" },
  { id: "kick", name: "Kick", icon: Music, color: "text-green-600" },
  { id: "twitter", name: "Twitter", icon: Twitter, color: "text-blue-400" },
  { id: "instagram", name: "Instagram", icon: Instagram, color: "text-pink-600" },
  { id: "tiktok", name: "TikTok", icon: Music, color: "text-black" },
  { id: "snapchat", name: "Snapchat", icon: Camera, color: "text-yellow-500" },
];

interface SocialLink {
  id: string;
  guild_id: string;
  platform: string;
  url: string;
  channel_id?: string;
  role_id?: string;
  custom_message?: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
  statistics: {
    total_posts: number;
    last_posted?: string;
  };
}

interface SocialLimits {
  guild_id: string;
  free_links: { [key: string]: number };
  purchased_links: { [key: string]: number };
  used_links: { [key: string]: number };
  remaining_links: { [key: string]: number };
  total_purchased: number;
  total_used: number;
}

interface RecentPost {
  platform: string;
  title: string;
  url: string;
  posted_at: string;
  channel_name: string;
}

export default function SocialIntegrationPage() {
  const params = useParams();
  const guildId = params.id as string;

  const [links, setLinks] = useState<SocialLink[]>([]);
  const [limits, setLimits] = useState<SocialLimits | null>(null);
  const [recentPosts, setRecentPosts] = useState<RecentPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string>("");

  const [newLink, setNewLink] = useState({
    platform: "",
    url: "",
    channel_id: "",
    role_id: "",
    custom_message: "",
  });

  useEffect(() => {
    fetchLinks();
    fetchLimits();
    fetchRecentPosts();
  }, [guildId]);

  const fetchLinks = async () => {
    try {
      const response = await fetch(`/api/social/guilds/${guildId}/links`, {
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setLinks(data);
      }
    } catch (error) {
      console.error("Failed to fetch links:", error);
    }
  };

  const fetchLimits = async () => {
    try {
      const response = await fetch(`/api/social/guilds/${guildId}/limits`, {
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setLimits(data);
      }
    } catch (error) {
      console.error("Failed to fetch limits:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentPosts = async () => {
    try {
      const response = await fetch(`/api/social/guilds/${guildId}/posts?limit=10`, {
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRecentPosts(data);
      }
    } catch (error) {
      console.error("Failed to fetch recent posts:", error);
    }
  };

  const handleCreateLink = async () => {
    if (!newLink.platform || !newLink.url) {
      alert("Please select a platform and provide a URL");
      return;
    }

    try {
      const response = await fetch(`/api/social/guilds/${guildId}/links`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
        body: JSON.stringify(newLink),
      });

      if (response.ok) {
        alert("Link added successfully!");
        setIsCreating(false);
        resetForm();
        fetchLinks();
        fetchLimits();
      } else {
        const error = await response.json();
        alert(`Failed to add link: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error creating link:", error);
      alert("Error creating link");
    }
  };

  const handleToggleLink = async (linkId: string) => {
    try {
      const response = await fetch(`/api/social/guilds/${guildId}/links/${linkId}/toggle`, {
        method: "PATCH",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });

      if (response.ok) {
        fetchLinks();
      }
    } catch (error) {
      console.error("Error toggling link:", error);
    }
  };

  const handleDeleteLink = async (linkId: string) => {
    if (!confirm("Are you sure you want to delete this link?")) return;

    try {
      const response = await fetch(`/api/social/guilds/${guildId}/links/${linkId}`, {
        method: "DELETE",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });

      if (response.ok) {
        alert("Link deleted successfully");
        fetchLinks();
        fetchLimits();
      }
    } catch (error) {
      console.error("Error deleting link:", error);
    }
  };

  const handlePurchaseLink = async (platform: string) => {
    if (!confirm(`Purchase an additional ${platform} link for 200 credits?`)) return;

    try {
      const response = await fetch(`/api/social/guilds/${guildId}/purchase`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
        body: JSON.stringify({ platform }),
      });

      if (response.ok) {
        alert("Link purchased successfully!");
        fetchLimits();
      } else {
        const error = await response.json();
        alert(`Purchase failed: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error purchasing link:", error);
      alert("Error purchasing link");
    }
  };

  const resetForm = () => {
    setNewLink({
      platform: "",
      url: "",
      channel_id: "",
      role_id: "",
      custom_message: "",
    });
  };

  const getPlatformInfo = (platformId: string) => {
    return PLATFORMS.find(p => p.id === platformId) || PLATFORMS[0];
  };

  const getLinksForPlatform = (platformId: string) => {
    return links.filter(link => link.platform === platformId);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading social integration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🔗 Social Integration</h1>
        <p className="text-gray-600">Connect and monitor your social media platforms</p>
      </div>

      {/* Limits Overview */}
      {limits && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Link Limits Overview</CardTitle>
            <CardDescription>Track your usage across all platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{limits.total_used}</div>
                <div className="text-sm text-gray-600">Total Used</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{limits.total_purchased}</div>
                <div className="text-sm text-gray-600">Total Purchased</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{links.filter(l => l.enabled).length}</div>
                <div className="text-sm text-gray-600">Active Links</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{recentPosts.length}</div>
                <div className="text-sm text-gray-600">Recent Posts</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-4">
          <Badge variant="outline">{links.length} Total Links</Badge>
          <Badge variant="outline">{links.filter(l => l.enabled).length} Active</Badge>
        </div>
        <Dialog open={isCreating} onOpenChange={setIsCreating}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Link
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add Social Media Link</DialogTitle>
              <DialogDescription>
                Connect a social media platform to post notifications
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div>
                <Label>Platform *</Label>
                <Select
                  value={newLink.platform}
                  onValueChange={(value) => setNewLink({ ...newLink, platform: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select platform..." />
                  </SelectTrigger>
                  <SelectContent>
                    {PLATFORMS.map((platform) => {
                      const Icon = platform.icon;
                      const remaining = limits?.remaining_links[platform.id] || 0;
                      return (
                        <SelectItem 
                          key={platform.id} 
                          value={platform.id}
                          disabled={remaining <= 0}
                        >
                          <div className="flex items-center gap-2">
                            <Icon className={`w-4 h-4 ${platform.color}`} />
                            <span>{platform.name}</span>
                            <span className="text-xs text-gray-500">
                              ({remaining} remaining)
                            </span>
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="url">URL *</Label>
                <Input
                  id="url"
                  value={newLink.url}
                  onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
                  placeholder="https://..."
                />
              </div>

              <div>
                <Label htmlFor="channel_id">Notification Channel ID (Optional)</Label>
                <Input
                  id="channel_id"
                  value={newLink.channel_id}
                  onChange={(e) => setNewLink({ ...newLink, channel_id: e.target.value })}
                  placeholder="1234567890"
                />
              </div>

              <div>
                <Label htmlFor="role_id">Mention Role ID (Optional)</Label>
                <Input
                  id="role_id"
                  value={newLink.role_id}
                  onChange={(e) => setNewLink({ ...newLink, role_id: e.target.value })}
                  placeholder="1234567890"
                />
              </div>

              <div>
                <Label htmlFor="custom_message">Custom Message (Optional)</Label>
                <Textarea
                  id="custom_message"
                  value={newLink.custom_message}
                  onChange={(e) => setNewLink({ ...newLink, custom_message: e.target.value })}
                  placeholder="New post from {creator}!"
                  rows={3}
                />
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => { setIsCreating(false); resetForm(); }}>
                Cancel
              </Button>
              <Button onClick={handleCreateLink}>
                Add Link
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Platform Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {PLATFORMS.map((platform) => {
          const Icon = platform.icon;
          const platformLinks = getLinksForPlatform(platform.id);
          const remaining = limits?.remaining_links[platform.id] || 0;
          const used = limits?.used_links[platform.id] || 0;
          const purchased = limits?.purchased_links[platform.id] || 0;
          const free = limits?.free_links[platform.id] || 0;

          return (
            <Card key={platform.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon className={`w-6 h-6 ${platform.color}`} />
                    <CardTitle className="text-lg">{platform.name}</CardTitle>
                  </div>
                  <Badge variant={remaining > 0 ? "default" : "secondary"}>
                    {remaining} left
                  </Badge>
                </div>
                <CardDescription>
                  {used}/{free + purchased} links used
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {platformLinks.length > 0 ? (
                    <div className="space-y-2 mb-3">
                      {platformLinks.map((link) => (
                        <div key={link.id} className="p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1 min-w-0">
                              <a 
                                href={link.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:underline flex items-center gap-1 truncate"
                              >
                                <span className="truncate">{link.url}</span>
                                <ExternalLink className="w-3 h-3 flex-shrink-0" />
                              </a>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge variant={link.enabled ? "default" : "secondary"} className="text-xs">
                                  {link.enabled ? "Active" : "Disabled"}
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  {link.statistics.total_posts} posts
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex gap-1">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleLink(link.id)}
                              className="flex-1"
                            >
                              <Power className="w-3 h-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteLink(link.id)}
                            >
                              <Trash2 className="w-3 h-3 text-red-500" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-4 text-sm text-gray-500">
                      No links added yet
                    </div>
                  )}

                  {remaining <= 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePurchaseLink(platform.id)}
                      className="w-full"
                    >
                      <ShoppingCart className="w-4 h-4 mr-2" />
                      Buy Link (200 Credits)
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Posts */}
      {recentPosts.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Recent Posts
            </CardTitle>
            <CardDescription>Latest activity from your connected platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentPosts.map((post, index) => {
                const platformInfo = getPlatformInfo(post.platform);
                const Icon = platformInfo.icon;
                
                return (
                  <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <Icon className={`w-5 h-5 ${platformInfo.color} flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <a 
                        href={post.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm font-medium hover:underline truncate block"
                      >
                        {post.title}
                      </a>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-600">{post.channel_name}</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">
                          {new Date(post.posted_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <ExternalLink className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {links.length === 0 && (
        <Card className="mt-6">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ExternalLink className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-4">No social media links connected yet</p>
            <Button onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Link
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
