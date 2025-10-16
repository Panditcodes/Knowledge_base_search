import { useState } from "react";
import { Search, Loader2, Copy, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { queryKnowledgeBase } from "@/services/api";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Query = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string>("");
  const [sources, setSources] = useState<any[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [topK, setTopK] = useState(5);
  const [temperature, setTemperature] = useState(0.3);  // Optimized for structured responses
  const [maxTokens, setMaxTokens] = useState(2048);  // Increased for comprehensive answers
  const { toast } = useToast();

  const handleQuery = async () => {
    if (!query.trim()) {
      toast({
        title: "Empty query",
        description: "Please enter a question",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await queryKnowledgeBase({
        query,
        top_k: topK,
        temperature,
        max_tokens: maxTokens,
      });

      setAnswer(response.answer);
      setSources(response.sources || []);

      toast({
        title: "Query successful",
        description: `Retrieved ${response.sources?.length || 0} sources`,
      });
    } catch (error: any) {
      toast({
        title: "Query failed",
        description: error.message || "Something went wrong",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(answer);
    toast({
      title: "Copied!",
      description: "Answer copied to clipboard",
    });
  };

  return (
    <div className="min-h-screen animate-fade-in">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="mb-8 animate-slide-up">
          <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent gradient-primary bg-gradient-to-r from-primary to-primary-dark">
            Ask Questions
          </h1>
          <p className="text-muted-foreground text-lg">
            Query your knowledge base with AI-powered search
          </p>
        </div>

        {/* Query Input */}
        <div className="bg-card rounded-xl shadow-lg p-6 mb-6 animate-scale-in">
          <label className="block text-sm font-medium mb-3">
            Your Question
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What would you like to know?"
            rows={4}
            className="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.ctrlKey) {
                handleQuery();
              }
            }}
          />
          <p className="text-xs text-muted-foreground mt-2">
            Press Ctrl+Enter to search
          </p>

          {/* Advanced Settings */}
          <div className="mt-6">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center space-x-2 text-sm font-medium text-primary hover:text-primary-dark transition-colors"
            >
              {showAdvanced ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
              <span>Advanced Settings</span>
            </button>

            {showAdvanced && (
              <div className="mt-4 space-y-4 p-4 bg-muted/30 rounded-lg animate-slide-up">
                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium">
                      Top-K Results
                    </label>
                    <span className="text-sm text-muted-foreground">{topK}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="w-full accent-primary"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium">Temperature</label>
                    <span className="text-sm text-muted-foreground">
                      {temperature.toFixed(2)}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(Number(e.target.value))}
                    className="w-full accent-primary"
                  />
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-sm font-medium">Max Tokens</label>
                    <span className="text-sm text-muted-foreground">
                      {maxTokens}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="512"
                    max="4096"
                    step="128"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(Number(e.target.value))}
                    className="w-full accent-primary"
                  />
                </div>
              </div>
            )}
          </div>

          <button
            onClick={handleQuery}
            disabled={loading || !query.trim()}
            className="w-full mt-6 px-6 py-4 gradient-primary text-primary-foreground rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow hover:scale-[1.02] transition-all flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin-smooth" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                <span>Search Knowledge Base</span>
              </>
            )}
          </button>
        </div>

        {/* Answer Display */}
        {answer && (
          <div className="bg-card rounded-xl shadow-lg p-6 mb-6 animate-slide-up">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Answer</h2>
              </div>
              <button
                onClick={copyToClipboard}
                className="flex items-center space-x-2 px-3 py-2 text-sm bg-muted hover:bg-muted/80 rounded-lg transition-all hover:scale-105"
              >
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </button>
            </div>

            <div className="prose prose-sm max-w-none dark:prose-invert text-foreground leading-relaxed">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({node, ...props}) => <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />,
                  h2: ({node, ...props}) => <h2 className="text-xl font-bold mt-5 mb-3" {...props} />,
                  h3: ({node, ...props}) => <h3 className="text-lg font-semibold mt-4 mb-2" {...props} />,
                  p: ({node, ...props}) => <p className="mb-3 leading-relaxed" {...props} />,
                  ul: ({node, ...props}) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
                  li: ({node, ...props}) => <li className="ml-2" {...props} />,
                  strong: ({node, ...props}) => <strong className="font-bold text-foreground" {...props} />,
                  code: ({node, inline, ...props}: any) => 
                    inline ? (
                      <code className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono" {...props} />
                    ) : (
                      <code className="block p-3 bg-muted rounded-lg text-sm font-mono overflow-x-auto my-2" {...props} />
                    ),
                  blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-primary pl-4 italic my-3" {...props} />,
                }}
              >
                {answer}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Sources */}
        {sources.length > 0 && (
          <div className="animate-slide-up">
            <h2 className="text-xl font-semibold mb-4">
              Sources ({sources.length})
            </h2>
            <div className="space-y-3">
              {sources.map((source, index) => (
                <div
                  key={index}
                  className="bg-card p-5 rounded-xl shadow-md hover:shadow-lg transition-all border-l-4 border-primary"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-1 text-xs font-medium bg-primary/10 text-primary rounded">
                        Source {index + 1}
                      </span>
                      <span className="px-2 py-1 text-xs font-medium gradient-secondary text-accent-foreground rounded">
                        {(source.score * 100).toFixed(1)}% match
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-foreground/80 leading-relaxed">
                    {source.text}
                  </p>
                  {source.metadata && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {Object.entries(source.metadata).map(([key, value]) => (
                        <span
                          key={key}
                          className="px-2 py-1 text-xs bg-muted rounded"
                        >
                          {key}: {String(value)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!answer && !loading && (
          <div className="text-center py-12 animate-fade-in">
            <Search className="w-16 h-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-xl font-semibold mb-2 text-muted-foreground">
              No results yet
            </h3>
            <p className="text-muted-foreground">
              Enter a question and search to get started
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Query;
