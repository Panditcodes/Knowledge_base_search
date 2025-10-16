import { useState, useCallback } from "react";
import { Upload as UploadIcon, File, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { uploadFile, checkStatus } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const Upload = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [sourceName, setSourceName] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) =>
      ["application/pdf", "text/plain", "text/markdown"].includes(file.type)
    );

    if (droppedFiles.length > 0) {
      setFiles((prev) => [...prev, ...droppedFiles]);
      toast({
        title: "Files added",
        description: `${droppedFiles.length} file(s) ready to upload`,
      });
    }
  }, [toast]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const pollStatus = async (taskId: string) => {
    const maxAttempts = 30;
    let attempts = 0;

    const poll = async () => {
      try {
        const status = await checkStatus(taskId);
        
        if (status.status === "completed") {
          setProgress(100);
          toast({
            title: "Upload successful!",
            description: "Your document has been processed and indexed.",
          });
          setFiles([]);
          setSourceName("");
          setUploading(false);
        } else if (status.status === "failed") {
          throw new Error(status.error || "Processing failed");
        } else {
          attempts++;
          setProgress(Math.min(90, attempts * 3));
          if (attempts < maxAttempts) {
            setTimeout(poll, 2000);
          } else {
            throw new Error("Processing timeout");
          }
        }
      } catch (error: any) {
        toast({
          title: "Upload failed",
          description: error.message || "Something went wrong",
          variant: "destructive",
        });
        setUploading(false);
      }
    };

    poll();
  };

  const handleUpload = async () => {
    if (files.length === 0 || !sourceName.trim()) {
      toast({
        title: "Missing information",
        description: "Please select files and provide a source name",
        variant: "destructive",
      });
      return;
    }

    setUploading(true);
    setProgress(0);

    try {
      for (const file of files) {
        const response = await uploadFile(file, sourceName);
        await pollStatus(response.task_id);
      }
    } catch (error: any) {
      toast({
        title: "Upload failed",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen animate-fade-in">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8 animate-slide-up">
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent gradient-primary bg-gradient-to-r from-primary to-primary-dark">
            Upload Documents
          </h1>
          <p className="text-muted-foreground text-lg">
            Add PDF, TXT, or MD files to your knowledge base
          </p>
        </div>

        {/* Upload Zone */}
        <div className="bg-card rounded-xl shadow-lg p-8 mb-6 animate-scale-in">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
              dragActive
                ? "border-primary bg-primary/5 shadow-glow"
                : "border-border hover:border-primary/50 hover:bg-muted/50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <UploadIcon className="w-16 h-16 mx-auto mb-4 text-primary" />
            <h3 className="text-xl font-semibold mb-2">
              Drag & Drop Files Here
            </h3>
            <p className="text-muted-foreground mb-4">
              or click to browse (PDF, TXT, MD)
            </p>
            <input
              type="file"
              id="file-input"
              className="hidden"
              multiple
              accept=".pdf,.txt,.md"
              onChange={handleFileInput}
            />
            <label
              htmlFor="file-input"
              className="inline-block px-6 py-3 gradient-primary text-primary-foreground rounded-lg font-medium cursor-pointer hover:shadow-glow hover:scale-105 transition-all"
            >
              Browse Files
            </label>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-6 space-y-3 animate-slide-up">
              <h4 className="font-semibold text-sm text-muted-foreground uppercase">
                Selected Files ({files.length})
              </h4>
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <File className="w-5 h-5 text-primary" />
                    <div>
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="text-destructive hover:text-destructive/80 hover:scale-110 transition-all"
                  >
                    <XCircle className="w-5 h-5" />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Source Name Input */}
          <div className="mt-6">
            <label className="block text-sm font-medium mb-2">
              Source Name
            </label>
            <input
              type="text"
              value={sourceName}
              onChange={(e) => setSourceName(e.target.value)}
              placeholder="e.g., Product Documentation, Research Papers"
              className="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
            />
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={uploading || files.length === 0 || !sourceName.trim()}
            className="w-full mt-6 px-6 py-4 gradient-primary text-primary-foreground rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow hover:scale-[1.02] transition-all flex items-center justify-center space-x-2"
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin-smooth" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <UploadIcon className="w-5 h-5" />
                <span>Upload & Process</span>
              </>
            )}
          </button>

          {/* Progress Bar */}
          {uploading && (
            <div className="mt-6 animate-slide-up">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-muted-foreground">Processing</span>
                <span className="font-medium">{progress}%</span>
              </div>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full gradient-primary transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-slide-up">
          <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
            <div className="w-12 h-12 rounded-lg gradient-primary flex items-center justify-center mb-3">
              <File className="w-6 h-6 text-primary-foreground" />
            </div>
            <h3 className="font-semibold mb-1">Supported Formats</h3>
            <p className="text-sm text-muted-foreground">
              PDF, TXT, and Markdown files
            </p>
          </div>

          <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
            <div className="w-12 h-12 rounded-lg gradient-secondary flex items-center justify-center mb-3">
              <CheckCircle className="w-6 h-6 text-accent-foreground" />
            </div>
            <h3 className="font-semibold mb-1">Auto Processing</h3>
            <p className="text-sm text-muted-foreground">
              Documents are automatically indexed
            </p>
          </div>

          <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-3">
              <Loader2 className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-1">Real-time Status</h3>
            <p className="text-sm text-muted-foreground">
              Track processing progress live
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;
