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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Power, 
  MessageSquare, 
  Zap,
  List,
  Settings,
  Palette,
  Square,
  ChevronDown
} from "lucide-react";

interface Embed {
  title?: string;
  description?: string;
  color?: number;
  footer_text?: string;
  footer_icon?: string;
  thumbnail?: string;
  image?: string;
  author_name?: string;
  author_icon?: string;
  timestamp?: boolean;
}

interface Button {
  custom_id: string;
  label: string;
  style: "primary" | "secondary" | "success" | "danger" | "link";
  emoji?: string;
  url?: string;
  disabled?: boolean;
}

interface DropdownOption {
  value: string;
  label: string;
  description?: string;
  emoji?: string;
  default?: boolean;
}

interface Dropdown {
  custom_id: string;
  placeholder: string;
  min_values: number;
  max_values: number;
  options: DropdownOption[];
}

interface AutoMessage {
  id: string;
  guild_id: string;
  name: string;
  trigger_type: "keyword" | "button" | "dropdown";
  trigger_value: string;
  response_type: "text" | "embed" | "both";
  text_response?: string;
  embed_response?: Embed;
  buttons?: Button[];
  dropdowns?: Dropdown[];
  allowed_roles?: string[];
  allowed_channels?: string[];
  case_sensitive: boolean;
  exact_match: boolean;
  delete_trigger: boolean;
  dm_response: boolean;
  enabled: boolean;
  created_at: string;
  updated_at: string;
  statistics: {
    total_triggers: number;
    last_triggered?: string;
  };
}

export default function AutoMessagesPage() {
  const params = useParams();
  const guildId = params.id as string;

  const [messages, setMessages] = useState<AutoMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState<AutoMessage | null>(null);

  const [newMessage, setNewMessage] = useState({
    name: "",
    trigger_type: "keyword" as "keyword" | "button" | "dropdown",
    trigger_value: "",
    response_type: "text" as "text" | "embed" | "both",
    text_response: "",
    embed_response: {} as Embed,
    buttons: [] as Button[],
    case_sensitive: false,
    exact_match: false,
    delete_trigger: false,
    dm_response: false,
  });

  // Embed Builder State
  const [embedBuilder, setEmbedBuilder] = useState<Embed>({
    title: "",
    description: "",
    color: 0x5865F2,
  });

  // Button Builder State
  const [newButton, setNewButton] = useState<Button>({
    custom_id: "",
    label: "",
    style: "primary",
  });

  useEffect(() => {
    fetchMessages();
  }, [guildId]);

  const fetchMessages = async () => {
    try {
      const response = await fetch(`/api/automessages/guilds/${guildId}/messages`, {
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error("Failed to fetch messages:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMessage = async () => {
    if (!newMessage.name || !newMessage.trigger_value) {
      alert("Please fill in required fields");
      return;
    }

    if (newMessage.response_type === "text" && !newMessage.text_response) {
      alert("Text response is required");
      return;
    }

    if (newMessage.response_type === "embed" && !embedBuilder.title && !embedBuilder.description) {
      alert("Embed must have at least a title or description");
      return;
    }

    try {
      const payload = {
        ...newMessage,
        embed_response: newMessage.response_type === "embed" || newMessage.response_type === "both" 
          ? embedBuilder 
          : undefined,
      };

      const response = await fetch(`/api/automessages/guilds/${guildId}/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        alert("Message created successfully!");
        setIsCreating(false);
        resetForm();
        fetchMessages();
      } else {
        const error = await response.json();
        alert(`Failed to create message: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error creating message:", error);
      alert("Error creating message");
    }
  };

  const handleToggleMessage = async (messageId: string) => {
    try {
      const response = await fetch(`/api/automessages/guilds/${guildId}/messages/${messageId}/toggle`, {
        method: "PATCH",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });

      if (response.ok) {
        fetchMessages();
      }
    } catch (error) {
      console.error("Error toggling message:", error);
    }
  };

  const handleDeleteMessage = async (messageId: string) => {
    if (!confirm("Are you sure you want to delete this message?")) return;

    try {
      const response = await fetch(`/api/automessages/guilds/${guildId}/messages/${messageId}`, {
        method: "DELETE",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });

      if (response.ok) {
        alert("Message deleted successfully");
        fetchMessages();
      }
    } catch (error) {
      console.error("Error deleting message:", error);
    }
  };

  const addButton = () => {
    if (!newButton.label || !newButton.custom_id) {
      alert("Please fill in button label and custom ID");
      return;
    }

    setNewMessage({
      ...newMessage,
      buttons: [...(newMessage.buttons || []), newButton]
    });

    setNewButton({
      custom_id: "",
      label: "",
      style: "primary",
    });
  };

  const removeButton = (index: number) => {
    const updatedButtons = newMessage.buttons?.filter((_, i) => i !== index) || [];
    setNewMessage({ ...newMessage, buttons: updatedButtons });
  };

  const resetForm = () => {
    setNewMessage({
      name: "",
      trigger_type: "keyword",
      trigger_value: "",
      response_type: "text",
      text_response: "",
      embed_response: {} as Embed,
      buttons: [],
      case_sensitive: false,
      exact_match: false,
      delete_trigger: false,
      dm_response: false,
    });
    setEmbedBuilder({
      title: "",
      description: "",
      color: 0x5865F2,
    });
  };

  const getButtonStyle = (style: string) => {
    const styles = {
      primary: "bg-blue-600 text-white",
      secondary: "bg-gray-600 text-white",
      success: "bg-green-600 text-white",
      danger: "bg-red-600 text-white",
      link: "bg-transparent text-blue-600 underline",
    };
    return styles[style as keyof typeof styles] || styles.primary;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading auto messages...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">🤖 Auto-Messages System</h1>
        <p className="text-gray-600">Create automated responses with triggers, embeds, and buttons</p>
      </div>

      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <Badge variant="outline">{messages.length} Messages</Badge>
            <Badge variant="outline">{messages.filter(m => m.enabled).length} Active</Badge>
          </div>
        </div>
        <Dialog open={isCreating} onOpenChange={setIsCreating}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Message
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Auto Message</DialogTitle>
              <DialogDescription>
                Create an automated message with custom triggers and responses
              </DialogDescription>
            </DialogHeader>

            <Tabs defaultValue="basic" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="basic">Basic</TabsTrigger>
                <TabsTrigger value="embed">Embed</TabsTrigger>
                <TabsTrigger value="buttons">Buttons</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
              </TabsList>

              {/* Basic Tab */}
              <TabsContent value="basic" className="space-y-4">
                <div>
                  <Label htmlFor="name">Message Name *</Label>
                  <Input
                    id="name"
                    value={newMessage.name}
                    onChange={(e) => setNewMessage({ ...newMessage, name: e.target.value })}
                    placeholder="e.g., Welcome Message"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Trigger Type</Label>
                    <Select
                      value={newMessage.trigger_type}
                      onValueChange={(value) => setNewMessage({ ...newMessage, trigger_type: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="keyword">Keyword</SelectItem>
                        <SelectItem value="button">Button</SelectItem>
                        <SelectItem value="dropdown">Dropdown</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label>Trigger Value *</Label>
                    <Input
                      value={newMessage.trigger_value}
                      onChange={(e) => setNewMessage({ ...newMessage, trigger_value: e.target.value })}
                      placeholder={
                        newMessage.trigger_type === "keyword" ? "!hello" :
                        newMessage.trigger_type === "button" ? "button_id" :
                        "dropdown_value"
                      }
                    />
                  </div>
                </div>

                <div>
                  <Label>Response Type</Label>
                  <Select
                    value={newMessage.response_type}
                    onValueChange={(value) => setNewMessage({ ...newMessage, response_type: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">Text Only</SelectItem>
                      <SelectItem value="embed">Embed Only</SelectItem>
                      <SelectItem value="both">Text + Embed</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {(newMessage.response_type === "text" || newMessage.response_type === "both") && (
                  <div>
                    <Label>Text Response *</Label>
                    <Textarea
                      value={newMessage.text_response}
                      onChange={(e) => setNewMessage({ ...newMessage, text_response: e.target.value })}
                      placeholder="The message text..."
                      rows={4}
                    />
                  </div>
                )}
              </TabsContent>

              {/* Embed Tab */}
              <TabsContent value="embed" className="space-y-4">
                <div>
                  <Label htmlFor="embed_title">Embed Title</Label>
                  <Input
                    id="embed_title"
                    value={embedBuilder.title}
                    onChange={(e) => setEmbedBuilder({ ...embedBuilder, title: e.target.value })}
                    placeholder="Embed title"
                  />
                </div>

                <div>
                  <Label htmlFor="embed_description">Embed Description</Label>
                  <Textarea
                    id="embed_description"
                    value={embedBuilder.description}
                    onChange={(e) => setEmbedBuilder({ ...embedBuilder, description: e.target.value })}
                    placeholder="Embed description..."
                    rows={4}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="embed_color">Color (Hex)</Label>
                    <div className="flex gap-2">
                      <Input
                        id="embed_color"
                        type="color"
                        value={`#${embedBuilder.color?.toString(16).padStart(6, '0')}`}
                        onChange={(e) => setEmbedBuilder({ ...embedBuilder, color: parseInt(e.target.value.slice(1), 16) })}
                        className="w-20"
                      />
                      <Input
                        value={`#${embedBuilder.color?.toString(16).padStart(6, '0').toUpperCase()}`}
                        readOnly
                        className="flex-1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="embed_thumbnail">Thumbnail URL</Label>
                    <Input
                      id="embed_thumbnail"
                      value={embedBuilder.thumbnail}
                      onChange={(e) => setEmbedBuilder({ ...embedBuilder, thumbnail: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="embed_author">Author Name</Label>
                    <Input
                      id="embed_author"
                      value={embedBuilder.author_name}
                      onChange={(e) => setEmbedBuilder({ ...embedBuilder, author_name: e.target.value })}
                      placeholder="Author name"
                    />
                  </div>

                  <div>
                    <Label htmlFor="embed_footer">Footer Text</Label>
                    <Input
                      id="embed_footer"
                      value={embedBuilder.footer_text}
                      onChange={(e) => setEmbedBuilder({ ...embedBuilder, footer_text: e.target.value })}
                      placeholder="Footer text"
                    />
                  </div>
                </div>

                {/* Embed Preview */}
                <div className="border rounded-lg p-4 bg-gray-50">
                  <h3 className="text-sm font-semibold mb-3">Preview</h3>
                  <div 
                    className="rounded-lg p-4 space-y-2"
                    style={{ 
                      borderLeft: `4px solid #${embedBuilder.color?.toString(16).padStart(6, '0')}`,
                      backgroundColor: 'white'
                    }}
                  >
                    {embedBuilder.author_name && (
                      <div className="flex items-center gap-2 text-sm font-medium">
                        {embedBuilder.author_name}
                      </div>
                    )}
                    {embedBuilder.title && (
                      <div className="font-bold text-lg">{embedBuilder.title}</div>
                    )}
                    {embedBuilder.description && (
                      <div className="text-sm text-gray-700">{embedBuilder.description}</div>
                    )}
                    {embedBuilder.footer_text && (
                      <div className="text-xs text-gray-500 pt-2">{embedBuilder.footer_text}</div>
                    )}
                  </div>
                </div>
              </TabsContent>

              {/* Buttons Tab */}
              <TabsContent value="buttons" className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Buttons ({newMessage.buttons?.length || 0}/25)</h3>
                  
                  {newMessage.buttons && newMessage.buttons.length > 0 && (
                    <div className="space-y-2 mb-4">
                      {newMessage.buttons.map((button, index) => (
                        <div key={index} className="flex items-center gap-2 p-3 bg-gray-50 rounded">
                          <div className={`px-4 py-2 rounded ${getButtonStyle(button.style)} text-sm font-medium`}>
                            {button.label}
                          </div>
                          <div className="flex-1 text-sm text-gray-600">
                            ID: {button.custom_id}
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeButton(index)}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="border rounded-lg p-4 space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor="button_label">Button Label</Label>
                        <Input
                          id="button_label"
                          value={newButton.label}
                          onChange={(e) => setNewButton({ ...newButton, label: e.target.value })}
                          placeholder="Click Me!"
                          maxLength={80}
                        />
                      </div>

                      <div>
                        <Label htmlFor="button_id">Custom ID</Label>
                        <Input
                          id="button_id"
                          value={newButton.custom_id}
                          onChange={(e) => setNewButton({ ...newButton, custom_id: e.target.value })}
                          placeholder="button_id"
                          maxLength={100}
                        />
                      </div>
                    </div>

                    <div>
                      <Label>Button Style</Label>
                      <Select
                        value={newButton.style}
                        onValueChange={(value) => setNewButton({ ...newButton, style: value as any })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="primary">Primary (Blue)</SelectItem>
                          <SelectItem value="secondary">Secondary (Gray)</SelectItem>
                          <SelectItem value="success">Success (Green)</SelectItem>
                          <SelectItem value="danger">Danger (Red)</SelectItem>
                          <SelectItem value="link">Link</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Button onClick={addButton} className="w-full">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Button
                    </Button>
                  </div>
                </div>
              </TabsContent>

              {/* Settings Tab */}
              <TabsContent value="settings" className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Case Sensitive</Label>
                      <p className="text-sm text-gray-500">Match trigger with exact case</p>
                    </div>
                    <Switch
                      checked={newMessage.case_sensitive}
                      onCheckedChange={(checked) => setNewMessage({ ...newMessage, case_sensitive: checked })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Exact Match</Label>
                      <p className="text-sm text-gray-500">Trigger must match exactly</p>
                    </div>
                    <Switch
                      checked={newMessage.exact_match}
                      onCheckedChange={(checked) => setNewMessage({ ...newMessage, exact_match: checked })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Delete Trigger</Label>
                      <p className="text-sm text-gray-500">Delete the trigger message</p>
                    </div>
                    <Switch
                      checked={newMessage.delete_trigger}
                      onCheckedChange={(checked) => setNewMessage({ ...newMessage, delete_trigger: checked })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>DM Response</Label>
                      <p className="text-sm text-gray-500">Send response via DM</p>
                    </div>
                    <Switch
                      checked={newMessage.dm_response}
                      onCheckedChange={(checked) => setNewMessage({ ...newMessage, dm_response: checked })}
                    />
                  </div>
                </div>
              </TabsContent>
            </Tabs>

            <DialogFooter>
              <Button variant="outline" onClick={() => { setIsCreating(false); resetForm(); }}>
                Cancel
              </Button>
              <Button onClick={handleCreateMessage}>
                Create Message
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Messages Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {messages.map((message) => (
          <Card key={message.id} className={!message.enabled ? "opacity-60" : ""}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">{message.name}</CardTitle>
                  <CardDescription className="mt-1">
                    <Badge variant="outline" className="mr-2">
                      {message.trigger_type}
                    </Badge>
                    <span className="text-xs">{message.trigger_value}</span>
                  </CardDescription>
                </div>
                <Badge variant={message.enabled ? "default" : "secondary"}>
                  {message.enabled ? "Active" : "Disabled"}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <MessageSquare className="w-4 h-4 text-gray-500" />
                  <span>Type: {message.response_type}</span>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <Zap className="w-4 h-4 text-gray-500" />
                  <span>{message.statistics.total_triggers} triggers</span>
                </div>

                {message.buttons && message.buttons.length > 0 && (
                  <div className="flex items-center gap-2 text-sm">
                    <Square className="w-4 h-4 text-gray-500" />
                    <span>{message.buttons.length} button(s)</span>
                  </div>
                )}

                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleToggleMessage(message.id)}
                    className="flex-1"
                  >
                    <Power className="w-4 h-4 mr-2" />
                    {message.enabled ? "Disable" : "Enable"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedMessage(message)}
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeleteMessage(message.id)}
                  >
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {messages.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <MessageSquare className="w-12 h-12 text-gray-400 mb-4" />
            <p className="text-gray-600 mb-4">No auto messages yet</p>
            <Button onClick={() => setIsCreating(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Message
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
