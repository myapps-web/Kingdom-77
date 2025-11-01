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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Plus, 
  Edit, 
  Trash2, 
  Eye, 
  Power, 
  FileText, 
  Users, 
  CheckCircle, 
  XCircle,
  Clock,
  ChevronRight
} from "lucide-react";

interface Question {
  id: string;
  question_text: string;
  question_type: "text" | "textarea" | "number" | "select" | "multiselect" | "yes_no";
  required: boolean;
  options?: string[];
  min_length?: number;
  max_length?: number;
  placeholder?: string;
}

interface ApplicationForm {
  id: string;
  guild_id: string;
  title: string;
  description: string;
  channel_id: string;
  accept_role_id?: string;
  cooldown_hours: number;
  max_submissions: number;
  questions: Question[];
  enabled: boolean;
  created_at: string;
  updated_at: string;
  statistics: {
    total_submissions: number;
    pending: number;
    approved: number;
    rejected: number;
  };
}

interface Submission {
  id: string;
  form_id: string;
  guild_id: string;
  user_id: string;
  answers: Array<{ question_id: string; answer: string }>;
  status: "pending" | "approved" | "rejected";
  submitted_at: string;
  reviewed_at?: string;
  reviewed_by?: string;
  review_reason?: string;
}

export default function ApplicationsPage() {
  const params = useParams();
  const guildId = params.id as string;

  const [forms, setForms] = useState<ApplicationForm[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [selectedForm, setSelectedForm] = useState<ApplicationForm | null>(null);
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("forms");

  // Form creation state
  const [isCreating, setIsCreating] = useState(false);
  const [newForm, setNewForm] = useState({
    title: "",
    description: "",
    channel_id: "",
    accept_role_id: "",
    cooldown_hours: 24,
    max_submissions: 1,
    questions: [] as Question[]
  });

  // Question builder state
  const [newQuestion, setNewQuestion] = useState<Partial<Question>>({
    question_text: "",
    question_type: "text",
    required: true,
  });

  useEffect(() => {
    fetchForms();
    fetchSubmissions();
  }, [guildId]);

  const fetchForms = async () => {
    try {
      const response = await fetch(`/api/applications/guilds/${guildId}/forms`, {
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setForms(data);
      }
    } catch (error) {
      console.error("Failed to fetch forms:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubmissions = async () => {
    try {
      const response = await fetch(`/api/applications/guilds/${guildId}/submissions`, {
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSubmissions(data);
      }
    } catch (error) {
      console.error("Failed to fetch submissions:", error);
    }
  };

  const handleCreateForm = async () => {
    if (!newForm.title || !newForm.channel_id || newForm.questions.length === 0) {
      alert("Please fill in all required fields and add at least one question");
      return;
    }

    try {
      const response = await fetch(`/api/applications/guilds/${guildId}/forms`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
        body: JSON.stringify(newForm),
      });

      if (response.ok) {
        alert("Form created successfully!");
        setIsCreating(false);
        setNewForm({
          title: "",
          description: "",
          channel_id: "",
          accept_role_id: "",
          cooldown_hours: 24,
          max_submissions: 1,
          questions: []
        });
        fetchForms();
      } else {
        alert("Failed to create form");
      }
    } catch (error) {
      console.error("Error creating form:", error);
      alert("Error creating form");
    }
  };

  const handleToggleForm = async (formId: string) => {
    try {
      const response = await fetch(`/api/applications/guilds/${guildId}/forms/${formId}/toggle`, {
        method: "PATCH",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });

      if (response.ok) {
        fetchForms();
      }
    } catch (error) {
      console.error("Error toggling form:", error);
    }
  };

  const handleDeleteForm = async (formId: string) => {
    if (!confirm("Are you sure you want to delete this form?")) return;

    try {
      const response = await fetch(`/api/applications/guilds/${guildId}/forms/${formId}`, {
        method: "DELETE",
        headers: {
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
      });

      if (response.ok) {
        alert("Form deleted successfully");
        fetchForms();
      }
    } catch (error) {
      console.error("Error deleting form:", error);
    }
  };

  const handleReviewSubmission = async (submissionId: string, status: "approved" | "rejected", reason?: string) => {
    try {
      const response = await fetch(`/api/applications/submissions/${submissionId}/review?reviewer_id=ADMIN_ID`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "",
        },
        body: JSON.stringify({ status, reason }),
      });

      if (response.ok) {
        alert(`Submission ${status} successfully`);
        fetchSubmissions();
        setSelectedSubmission(null);
      }
    } catch (error) {
      console.error("Error reviewing submission:", error);
    }
  };

  const addQuestion = () => {
    if (!newQuestion.question_text) {
      alert("Please enter a question text");
      return;
    }

    const question: Question = {
      id: `q${Date.now()}`,
      question_text: newQuestion.question_text,
      question_type: newQuestion.question_type as Question["question_type"],
      required: newQuestion.required || true,
      options: newQuestion.options,
      min_length: newQuestion.min_length,
      max_length: newQuestion.max_length,
      placeholder: newQuestion.placeholder,
    };

    setNewForm({
      ...newForm,
      questions: [...newForm.questions, question]
    });

    setNewQuestion({
      question_text: "",
      question_type: "text",
      required: true,
    });
  };

  const removeQuestion = (questionId: string) => {
    setNewForm({
      ...newForm,
      questions: newForm.questions.filter(q => q.id !== questionId)
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">📋 Applications System</h1>
        <p className="text-gray-600">Manage application forms and review submissions</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="forms">
            <FileText className="w-4 h-4 mr-2" />
            Forms ({forms.length})
          </TabsTrigger>
          <TabsTrigger value="submissions">
            <Users className="w-4 h-4 mr-2" />
            Submissions ({submissions.filter(s => s.status === "pending").length})
          </TabsTrigger>
        </TabsList>

        {/* Forms Tab */}
        <TabsContent value="forms" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Application Forms</h2>
            <Dialog open={isCreating} onOpenChange={setIsCreating}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Form
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create Application Form</DialogTitle>
                  <DialogDescription>
                    Create a new application form with custom questions
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title">Form Title *</Label>
                    <Input
                      id="title"
                      value={newForm.title}
                      onChange={(e) => setNewForm({ ...newForm, title: e.target.value })}
                      placeholder="e.g., Staff Application"
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description *</Label>
                    <Textarea
                      id="description"
                      value={newForm.description}
                      onChange={(e) => setNewForm({ ...newForm, description: e.target.value })}
                      placeholder="Describe what this application is for"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="channel_id">Submission Channel ID *</Label>
                      <Input
                        id="channel_id"
                        value={newForm.channel_id}
                        onChange={(e) => setNewForm({ ...newForm, channel_id: e.target.value })}
                        placeholder="123456789"
                      />
                    </div>

                    <div>
                      <Label htmlFor="accept_role_id">Accept Role ID (Optional)</Label>
                      <Input
                        id="accept_role_id"
                        value={newForm.accept_role_id}
                        onChange={(e) => setNewForm({ ...newForm, accept_role_id: e.target.value })}
                        placeholder="987654321"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="cooldown">Cooldown (hours)</Label>
                      <Input
                        id="cooldown"
                        type="number"
                        value={newForm.cooldown_hours}
                        onChange={(e) => setNewForm({ ...newForm, cooldown_hours: parseInt(e.target.value) })}
                      />
                    </div>

                    <div>
                      <Label htmlFor="max_submissions">Max Submissions</Label>
                      <Input
                        id="max_submissions"
                        type="number"
                        value={newForm.max_submissions}
                        onChange={(e) => setNewForm({ ...newForm, max_submissions: parseInt(e.target.value) })}
                      />
                    </div>
                  </div>

                  {/* Questions */}
                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-4">Questions ({newForm.questions.length})</h3>
                    
                    {newForm.questions.map((question, index) => (
                      <div key={question.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
                        <div className="flex-1">
                          <p className="font-medium">{index + 1}. {question.question_text}</p>
                          <p className="text-sm text-gray-500">
                            Type: {question.question_type} | Required: {question.required ? "Yes" : "No"}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeQuestion(question.id)}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    ))}

                    {/* Add Question */}
                    <div className="border rounded-lg p-4 space-y-3 mt-4">
                      <Input
                        placeholder="Question text"
                        value={newQuestion.question_text}
                        onChange={(e) => setNewQuestion({ ...newQuestion, question_text: e.target.value })}
                      />
                      
                      <div className="grid grid-cols-2 gap-2">
                        <Select
                          value={newQuestion.question_type}
                          onValueChange={(value) => setNewQuestion({ ...newQuestion, question_type: value as Question["question_type"] })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">Text</SelectItem>
                            <SelectItem value="textarea">Text Area</SelectItem>
                            <SelectItem value="number">Number</SelectItem>
                            <SelectItem value="select">Select</SelectItem>
                            <SelectItem value="multiselect">Multi-Select</SelectItem>
                            <SelectItem value="yes_no">Yes/No</SelectItem>
                          </SelectContent>
                        </Select>

                        <Button onClick={addQuestion} variant="outline">
                          <Plus className="w-4 h-4 mr-2" />
                          Add Question
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsCreating(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateForm}>
                    Create Form
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {forms.map((form) => (
              <Card key={form.id} className={!form.enabled ? "opacity-60" : ""}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{form.title}</CardTitle>
                      <CardDescription className="line-clamp-2 mt-1">
                        {form.description}
                      </CardDescription>
                    </div>
                    <Badge variant={form.enabled ? "default" : "secondary"}>
                      {form.enabled ? "Active" : "Disabled"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-2 text-gray-500" />
                        <span>{form.statistics.total_submissions} submissions</span>
                      </div>
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2 text-gray-500" />
                        <span>{form.cooldown_hours}h cooldown</span>
                      </div>
                    </div>

                    <div className="flex gap-2 text-sm">
                      <Badge variant="outline" className="text-yellow-600">
                        {form.statistics.pending} pending
                      </Badge>
                      <Badge variant="outline" className="text-green-600">
                        {form.statistics.approved} approved
                      </Badge>
                      <Badge variant="outline" className="text-red-600">
                        {form.statistics.rejected} rejected
                      </Badge>
                    </div>

                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleForm(form.id)}
                        className="flex-1"
                      >
                        <Power className="w-4 h-4 mr-2" />
                        {form.enabled ? "Disable" : "Enable"}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedForm(form)}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteForm(form.id)}
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {forms.length === 0 && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mb-4" />
                <p className="text-gray-600 mb-4">No application forms yet</p>
                <Button onClick={() => setIsCreating(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Form
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Submissions Tab */}
        <TabsContent value="submissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pending Submissions</CardTitle>
              <CardDescription>Review and approve or reject applications</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User ID</TableHead>
                    <TableHead>Form</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Submitted</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {submissions.filter(s => s.status === "pending").map((submission) => {
                    const form = forms.find(f => f.id === submission.form_id);
                    return (
                      <TableRow key={submission.id}>
                        <TableCell className="font-mono">{submission.user_id}</TableCell>
                        <TableCell>{form?.title || "Unknown"}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-yellow-600">
                            Pending
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {new Date(submission.submitted_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedSubmission(submission)}
                          >
                            <ChevronRight className="w-4 h-4 mr-2" />
                            Review
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>

              {submissions.filter(s => s.status === "pending").length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <p>No pending submissions</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Submission Review Dialog */}
      {selectedSubmission && (
        <Dialog open={!!selectedSubmission} onOpenChange={() => setSelectedSubmission(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Review Submission</DialogTitle>
              <DialogDescription>
                User ID: {selectedSubmission.user_id}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {selectedSubmission.answers.map((answer, index) => {
                const form = forms.find(f => f.id === selectedSubmission.form_id);
                const question = form?.questions.find(q => q.id === answer.question_id);
                return (
                  <div key={index} className="border-b pb-3">
                    <p className="font-medium text-sm text-gray-600 mb-1">
                      {question?.question_text || "Question"}
                    </p>
                    <p className="text-base">{answer.answer}</p>
                  </div>
                );
              })}
            </div>

            <DialogFooter className="gap-2">
              <Button
                variant="outline"
                onClick={() => setSelectedSubmission(null)}
              >
                Close
              </Button>
              <Button
                variant="destructive"
                onClick={() => handleReviewSubmission(selectedSubmission.id, "rejected", "Does not meet requirements")}
              >
                <XCircle className="w-4 h-4 mr-2" />
                Reject
              </Button>
              <Button
                onClick={() => handleReviewSubmission(selectedSubmission.id, "approved")}
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Approve
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
