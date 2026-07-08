import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { trpc } from "@/lib/trpc";
import {
  FileText,
  Link as LinkIcon,
  MessageSquare,
  Upload,
  Trash2,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Loader2,
  Plus,
  BookOpen,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import { useParams } from "wouter";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export default function KnowledgeBase() {
  const params = useParams<{ id: string }>();
  const agentId = parseInt(params.id || "0");
  const utils = trpc.useUtils();

  const { data: agent } = trpc.agent.get.useQuery({ id: agentId });
  const { data: sources = [], isLoading } = trpc.knowledge.list.useQuery({ agentId });
  const { data: trainingJobs = [] } = trpc.knowledge.getTrainingJobs.useQuery({ agentId });
  const { data: fileUploads = [] } = trpc.knowledge.listFiles.useQuery({ agentId });

  const [showAddDialog, setShowAddDialog] = useState(false);
  const [sourceType, setSourceType] = useState<"text" | "file" | "url" | "qa">("text");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const createMutation = trpc.knowledge.create.useMutation({
    onSuccess: () => {
      toast.success("Knowledge source added successfully");
      utils.knowledge.list.invalidate({ agentId });
      setShowAddDialog(false);
      resetForm();
    },
    onError: (error) => {
      toast.error(error.message || "Failed to add knowledge source");
    },
  });

  const processMutation = trpc.knowledge.process.useMutation({
    onSuccess: (data) => {
      toast.success(`Processed successfully! Created ${data.chunksCount} chunks`);
      utils.knowledge.list.invalidate({ agentId });
    },
    onError: (error) => {
      toast.error(error.message || "Failed to process knowledge source");
    },
  });

  const deleteMutation = trpc.knowledge.delete.useMutation({
    onSuccess: () => {
      toast.success("Knowledge source deleted");
      utils.knowledge.list.invalidate({ agentId });
      setDeleteId(null);
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete knowledge source");
    },
  });

  const trainMutation = trpc.knowledge.train.useMutation({
    onSuccess: () => {
      toast.success("Training started successfully");
      utils.knowledge.getTrainingJobs.invalidate({ agentId });
      utils.knowledge.list.invalidate({ agentId });
    },
    onError: (error) => {
      toast.error(error.message || "Failed to start training");
    },
  });

  const deleteFileMutation = trpc.knowledge.deleteFile.useMutation({
    onSuccess: () => {
      toast.success("File deleted successfully");
      utils.knowledge.listFiles.invalidate({ agentId });
      utils.knowledge.list.invalidate({ agentId });
    },
    onError: (error) => {
      toast.error(error.message || "Failed to delete file");
    },
  });

  const resetForm = () => {
    setTitle("");
    setContent("");
    setSourceUrl("");
    setSourceType("text");
    setSelectedFile(null);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a file");
      return;
    }

    if (!title.trim()) {
      toast.error("Please enter a title");
      return;
    }

    // Validate file size (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      toast.error("File size must be less than 10MB");
      return;
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain',
      'text/markdown'
    ];
    
    if (!allowedTypes.includes(selectedFile.type)) {
      toast.error("Invalid file type. Allowed: PDF, DOCX, DOC, TXT, MD");
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('agentId', agentId.toString());
      formData.append('title', title.trim());

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        toast.success(`File uploaded successfully! Processing ${data.filename}...`);
        utils.knowledge.list.invalidate({ agentId });
        setShowAddDialog(false);
        resetForm();
      } else {
        toast.error(data.error || "Failed to upload file");
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  const handleAddSource = () => {
    // Handle file upload separately
    if (sourceType === "file") {
      handleFileUpload();
      return;
    }

    if (!title.trim()) {
      toast.error("Please enter a title");
      return;
    }

    if (sourceType === "text" && !content.trim()) {
      toast.error("Please enter content");
      return;
    }

    if (sourceType === "url" && !sourceUrl.trim()) {
      toast.error("Please enter a URL");
      return;
    }

    createMutation.mutate({
      agentId,
      sourceType,
      title: title.trim(),
      content: content.trim() || undefined,
      sourceUrl: sourceUrl.trim() || undefined,
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "trained":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "processing":
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      trained: "default",
      processing: "secondary",
      error: "destructive",
      pending: "outline",
    };
    return (
      <Badge variant={variants[status] || "outline"}>
        {status}
      </Badge>
    );
  };

  const getSourceTypeIcon = (type: string) => {
    switch (type) {
      case "file":
        return <FileText className="h-4 w-4" />;
      case "url":
        return <LinkIcon className="h-4 w-4" />;
      case "qa":
        return <MessageSquare className="h-4 w-4" />;
      default:
        return <BookOpen className="h-4 w-4" />;
    }
  };

  const trainedCount = sources.filter(s => s.status === "trained").length;
  const totalCount = sources.length;
  const progressPercentage = totalCount > 0 ? (trainedCount / totalCount) * 100 : 0;

  const latestJob = trainingJobs[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-muted-foreground mt-1">
            Train {agent?.name || "your agent"} with custom knowledge sources
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => trainMutation.mutate({ agentId })}
            disabled={trainMutation.isPending || sources.filter(s => s.status === "pending").length === 0}
            variant="outline"
          >
            {trainMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Training...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Train Agent
              </>
            )}
          </Button>
          <Button onClick={() => setShowAddDialog(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Source
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sources</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalCount}</div>
            <p className="text-xs text-muted-foreground">
              {trainedCount} trained, {sources.filter(s => s.status === "pending").length} pending
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Training Progress</CardTitle>
            <Sparkles className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{progressPercentage.toFixed(0)}%</div>
            <Progress value={progressPercentage} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Training</CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {agent?.lastTrainedAt ? new Date(agent.lastTrainedAt).toLocaleDateString() : "Never"}
            </div>
            <p className="text-xs text-muted-foreground">
              {latestJob?.status === "completed" ? "Completed" : latestJob?.status === "processing" ? "In progress" : "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Knowledge Sources and Files Tabs */}
      <Tabs defaultValue="sources" className="space-y-4">
        <TabsList>
          <TabsTrigger value="sources">
            <BookOpen className="h-4 w-4 mr-2" />
            Knowledge Sources ({sources.length})
          </TabsTrigger>
          <TabsTrigger value="files">
            <FileText className="h-4 w-4 mr-2" />
            Uploaded Files ({fileUploads.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sources">
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Sources</CardTitle>
              <CardDescription>
                Manage the knowledge sources used to train your agent
              </CardDescription>
            </CardHeader>
            <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : sources.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No knowledge sources yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Add documents, text, or URLs to train your agent with custom knowledge
              </p>
              <Button onClick={() => setShowAddDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add First Source
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {sources.map((source) => (
                <div
                  key={source.id}
                  className="flex items-start gap-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="flex-shrink-0 mt-1">
                    {getSourceTypeIcon(source.sourceType)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium truncate">{source.title}</h4>
                      {getStatusBadge(source.status)}
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{source.sourceType.toUpperCase()}</span>
                      {(source.charactersCount ?? 0) > 0 && (
                        <span>{(source.charactersCount ?? 0).toLocaleString()} characters</span>
                      )}
                      {(source.chunksCount ?? 0) > 0 && (
                        <span>{source.chunksCount} chunks</span>
                      )}
                      <span>{new Date(source.createdAt).toLocaleDateString()}</span>
                    </div>
                    {source.errorMessage && (
                      <p className="text-xs text-red-500 mt-1">{source.errorMessage}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {source.status === "pending" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => processMutation.mutate({ sourceId: source.id })}
                        disabled={processMutation.isPending}
                      >
                        {processMutation.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <RefreshCw className="h-4 w-4 mr-1" />
                            Process
                          </>
                        )}
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setDeleteId(source.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
        </TabsContent>

        <TabsContent value="files">
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Files</CardTitle>
              <CardDescription>
                Manage files uploaded for knowledge training
              </CardDescription>
            </CardHeader>
            <CardContent>
              {fileUploads.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Upload className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No files uploaded yet</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Upload PDF, DOCX, or TXT files to train your agent
                  </p>
                  <Button onClick={() => {
                    setSourceType("file");
                    setShowAddDialog(true);
                  }}>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload First File
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {fileUploads.map((file) => (
                    <div
                      key={file.id}
                      className="flex items-start gap-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex-shrink-0 mt-1">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium truncate">{file.originalFilename}</h4>
                          {file.status === "completed" && (
                            <Badge variant="default" className="bg-green-500">
                              <CheckCircle2 className="mr-1 h-3 w-3" />
                              Processed
                            </Badge>
                          )}
                          {file.status === "processing" && (
                            <Badge variant="secondary">
                              <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                              Processing
                            </Badge>
                          )}
                          {file.status === "error" && (
                            <Badge variant="destructive">
                              <AlertCircle className="mr-1 h-3 w-3" />
                              Error
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{file.fileType.toUpperCase()}</span>
                          <span>{(file.fileSize / 1024).toFixed(2)} KB</span>
                          <span>{new Date(file.uploadedAt).toLocaleDateString()}</span>
                        </div>
                        {file.errorMessage && (
                          <p className="text-xs text-red-500 mt-1">{file.errorMessage}</p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            if (confirm("Are you sure you want to delete this file?")) {
                              deleteFileMutation.mutate({ id: file.id });
                            }
                          }}
                          disabled={deleteFileMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add Source Dialog */}
      {showAddDialog && (
        <div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl">
            <CardHeader>
              <CardTitle>Add Knowledge Source</CardTitle>
              <CardDescription>
                Add a new source to train your agent's knowledge base
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Source Type</Label>
                <Select value={sourceType} onValueChange={(v: any) => setSourceType(v)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="text">Text</SelectItem>
                    <SelectItem value="file">File</SelectItem>
                    <SelectItem value="url">URL</SelectItem>
                    <SelectItem value="qa">Q&A Pair</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Title</Label>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter a descriptive title"
                />
              </div>

              {sourceType === "url" && (
                <div>
                  <Label>URL</Label>
                  <Input
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    placeholder="https://example.com/document"
                  />
                </div>
              )}

              {sourceType === "file" && (
                <div>
                  <Label>File</Label>
                  <div className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      accept=".pdf,.docx,.doc,.txt,.md"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setSelectedFile(file);
                          if (!title) {
                            setTitle(file.name);
                          }
                        }
                      }}
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                      <p className="text-sm font-medium">
                        {selectedFile ? selectedFile.name : "Click to upload or drag and drop"}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        PDF, DOCX, DOC, TXT, MD (max 10MB)
                      </p>
                      {selectedFile && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Size: {(selectedFile.size / 1024).toFixed(2)} KB
                        </p>
                      )}
                    </label>
                  </div>
                </div>
              )}

              {(sourceType === "text" || sourceType === "qa") && (
                <div>
                  <Label>Content</Label>
                  <Textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Enter the content or knowledge..."
                    rows={8}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {content.length.toLocaleString()} characters
                  </p>
                </div>
              )}
            </CardContent>
            <div className="flex justify-end gap-2 p-6 pt-0">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAddDialog(false);
                  resetForm();
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddSource}
                disabled={createMutation.isPending || isUploading}
              >
                {(createMutation.isPending || isUploading) ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {isUploading ? 'Uploading...' : 'Adding...'}
                  </>
                ) : (
                  <>Add Source</>
                )}
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteId !== null} onOpenChange={() => setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Knowledge Source?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this knowledge source and all its embeddings.
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteId && deleteMutation.mutate({ id: deleteId })}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
