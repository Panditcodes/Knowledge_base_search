import { useState, useEffect } from "react";
import {
  Shield,
  Activity,
  Database,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";
import { getHealth, getStats, rebuildIndex } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const Admin = () => {
  const [apiKey, setApiKey] = useState("");
  const [health, setHealth] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    try {
      const healthData = await getHealth();
      setHealth(healthData);
    } catch (error: any) {
      toast({
        title: "Health check failed",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const fetchStats = async () => {
    if (!apiKey.trim()) {
      toast({
        title: "API key required",
        description: "Please enter your API key",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const statsData = await getStats(apiKey);
      setStats(statsData);
      toast({
        title: "Stats loaded",
        description: "Index statistics retrieved successfully",
      });
    } catch (error: any) {
      toast({
        title: "Failed to load stats",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    setRebuilding(true);
    try {
      const response = await rebuildIndex(apiKey);
      toast({
        title: "Index rebuilt",
        description: response.message,
      });
      setShowConfirm(false);
      fetchStats();
    } catch (error: any) {
      toast({
        title: "Rebuild failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setRebuilding(false);
    }
  };

  return (
    <div className="min-h-screen animate-fade-in">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8 animate-slide-up">
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent gradient-primary bg-gradient-to-r from-primary to-primary-dark">
            Admin Dashboard
          </h1>
          <p className="text-muted-foreground text-lg">
            Monitor system health and manage your knowledge base
          </p>
        </div>

        {/* API Key Input */}
        <div className="bg-card rounded-xl shadow-lg p-6 mb-6 animate-scale-in">
          <div className="flex items-center space-x-2 mb-4">
            <Shield className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">Authentication</h2>
          </div>
          <div className="flex space-x-3">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your API key"
              className="flex-1 px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
            />
            <button
              onClick={fetchStats}
              disabled={loading}
              className="px-6 py-3 gradient-primary text-primary-foreground rounded-lg font-semibold hover:shadow-glow hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin-smooth" />
              ) : (
                "Verify"
              )}
            </button>
          </div>
        </div>

        {/* System Health */}
        <div className="mb-6 animate-slide-up">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">System Health</h2>
          </div>

          {health ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">Jina Embeddings</h3>
                  {health.services?.jina ? (
                    <CheckCircle className="w-6 h-6 text-accent" />
                  ) : (
                    <XCircle className="w-6 h-6 text-destructive" />
                  )}
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-medium inline-block ${
                    health.services?.jina
                      ? "gradient-secondary text-accent-foreground"
                      : "bg-destructive/10 text-destructive"
                  }`}
                >
                  {health.services?.jina ? "Operational" : "Down"}
                </div>
              </div>

              <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">Pinecone Vector DB</h3>
                  {health.services?.pinecone ? (
                    <CheckCircle className="w-6 h-6 text-accent" />
                  ) : (
                    <XCircle className="w-6 h-6 text-destructive" />
                  )}
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-medium inline-block ${
                    health.services?.pinecone
                      ? "gradient-secondary text-accent-foreground"
                      : "bg-destructive/10 text-destructive"
                  }`}
                >
                  {health.services?.pinecone ? "Operational" : "Down"}
                </div>
              </div>

              <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">Groq LLM</h3>
                  {health.services?.groq ? (
                    <CheckCircle className="w-6 h-6 text-accent" />
                  ) : (
                    <XCircle className="w-6 h-6 text-destructive" />
                  )}
                </div>
                <div
                  className={`px-3 py-1 rounded-full text-sm font-medium inline-block ${
                    health.services?.groq
                      ? "gradient-secondary text-accent-foreground"
                      : "bg-destructive/10 text-destructive"
                  }`}
                >
                  {health.services?.groq ? "Operational" : "Down"}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-card p-12 rounded-xl shadow-md text-center">
              <Loader2 className="w-12 h-12 mx-auto mb-4 text-muted-foreground animate-spin-smooth" />
              <p className="text-muted-foreground">Loading health status...</p>
            </div>
          )}
        </div>

        {/* Index Statistics */}
        {stats && (
          <div className="mb-6 animate-slide-up">
            <div className="flex items-center space-x-2 mb-4">
              <Database className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold">Index Statistics</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                <div className="text-3xl font-bold gradient-primary bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-dark mb-2">
                  {stats.total_vectors?.toLocaleString() || 0}
                </div>
                <p className="text-muted-foreground">Total Vectors</p>
              </div>

              <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                <div className="text-3xl font-bold gradient-primary bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-dark mb-2">
                  {stats.index_size || "N/A"}
                </div>
                <p className="text-muted-foreground">Index Size</p>
              </div>

              <div className="bg-card p-6 rounded-xl shadow-md hover:shadow-lg transition-all">
                <div className="text-3xl font-bold gradient-primary bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary-dark mb-2">
                  {stats.namespaces?.length || 0}
                </div>
                <p className="text-muted-foreground">Namespaces</p>
              </div>
            </div>
          </div>
        )}

        {/* Rebuild Index */}
        <div className="bg-card rounded-xl shadow-lg p-6 animate-scale-in">
          <div className="flex items-center space-x-2 mb-4">
            <RefreshCw className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">Index Management</h2>
          </div>

          <p className="text-muted-foreground mb-4">
            Rebuild the entire knowledge base index. This will reprocess all
            documents and may take several minutes.
          </p>

          {!showConfirm ? (
            <button
              onClick={() => setShowConfirm(true)}
              disabled={!apiKey.trim()}
              className="px-6 py-3 bg-destructive text-destructive-foreground rounded-lg font-semibold hover:bg-destructive/90 hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Rebuild Index
            </button>
          ) : (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg animate-slide-up">
              <p className="font-medium mb-4 text-destructive">
                Are you sure? This action cannot be undone.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={handleRebuild}
                  disabled={rebuilding}
                  className="px-6 py-2 bg-destructive text-destructive-foreground rounded-lg font-semibold hover:bg-destructive/90 transition-all disabled:opacity-50 flex items-center space-x-2"
                >
                  {rebuilding ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin-smooth" />
                      <span>Rebuilding...</span>
                    </>
                  ) : (
                    <span>Confirm Rebuild</span>
                  )}
                </button>
                <button
                  onClick={() => setShowConfirm(false)}
                  className="px-6 py-2 bg-muted hover:bg-muted/80 rounded-lg font-semibold transition-all"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Admin;
