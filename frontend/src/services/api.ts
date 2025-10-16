import axios from "axios";

const API_BASE_URL = "http://localhost:8001";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface IngestResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  message?: string;
  error?: string;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  temperature?: number;
  max_tokens?: number;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    text: string;
    score: number;
    metadata: Record<string, any>;
  }>;
  tokens_used?: number;
}

export interface HealthResponse {
  status: string;
  services: {
    jina: boolean;
    pinecone: boolean;
    groq: boolean;
  };
}

export interface StatsResponse {
  total_vectors: number;
  index_size: string;
  namespaces: string[];
}

export const uploadFile = async (
  file: File,
  sourceName: string
): Promise<IngestResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("source_name", sourceName);

  const response = await api.post("/ingest", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const checkStatus = async (taskId: string): Promise<StatusResponse> => {
  const response = await api.get(`/ingest/${taskId}/status`);
  return response.data;
};

export const queryKnowledgeBase = async (
  request: QueryRequest
): Promise<QueryResponse> => {
  const response = await api.post("/query", request);
  return response.data;
};

export const getHealth = async (): Promise<HealthResponse> => {
  const response = await api.get("/health");
  return response.data;
};

export const getStats = async (apiKey: string): Promise<StatsResponse> => {
  const response = await api.get("/admin/stats", {
    headers: {
      "X-API-Key": apiKey,
    },
  });
  return response.data;
};

export const rebuildIndex = async (apiKey: string): Promise<{ message: string }> => {
  const response = await api.post(
    "/admin/rebuild-index",
    {},
    {
      headers: {
        "X-API-Key": apiKey,
      },
    }
  );
  return response.data;
};

export default api;
