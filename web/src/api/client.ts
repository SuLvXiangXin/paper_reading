import { apiUrl } from "./paths";

export type TreeNode = {
  name: string;
  path: string | null;
  kind: "directory" | "document";
  children: TreeNode[];
};

export type DocumentResponse = {
  path: string;
  domain: string;
  page_type: string;
  title: string;
  content: string;
  updated_at: number;
  size: number;
};

export type SearchResult = {
  path: string;
  title: string;
  snippet: string;
  score: number;
};

export type ContextDocument = {
  path: string;
  role: string;
  title: string;
  size: number;
};

export type ContextSnippet = {
  path: string;
  role: string;
  title: string;
  snippet: string;
};

export type ContextBundle = {
  page_path: string;
  domain: string;
  page_type: string;
  documents: ContextDocument[];
  snippets: ContextSnippet[];
  hash: string;
};

export type Conversation = {
  id: string;
  scope: string;
  domain: string | null;
  page_path: string | null;
  title: string;
  context_hash: string | null;
  created_at: string;
  updated_at: string;
  archived: boolean;
};

export type Message = {
  id: number;
  conversation_id: string;
  role: "user" | "assistant" | "tool" | "system";
  content: string;
  tool_calls_json: string | null;
  created_at: string;
};

export type Job = {
  id: string;
  conversation_id: string | null;
  kind: string;
  status: string;
  command_json: Record<string, unknown>;
  log_path: string;
  created_at: string;
  updated_at: string;
  return_code: number | null;
};

export type HomeResponse = {
  domain: string;
  recent_papers: SearchResult[];
  recent_reports: SearchResult[];
  git_status: string;
  model: string;
  provider_ready: boolean;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ ok: boolean; model: string; provider_ready: boolean }>("/api/health"),
  domains: () => request<{ domains: string[] }>("/api/domains"),
  tree: (domain: string) => request<TreeNode>(`/api/tree?domain=${encodeURIComponent(domain)}`),
  document: (path: string) => request<DocumentResponse>(`/api/document?path=${encodeURIComponent(path)}`),
  context: (path: string) => request<ContextBundle>(`/api/context/prepare?path=${encodeURIComponent(path)}`),
  search: (query: string, domain?: string) => {
    const params = new URLSearchParams({ q: query });
    if (domain) params.set("domain", domain);
    return request<{ results: SearchResult[] }>(`/api/search?${params.toString()}`);
  },
  home: (domain: string) => request<HomeResponse>(`/api/home?domain=${encodeURIComponent(domain)}`),
  conversation: (scope: string, domain: string, pagePath?: string) => {
    const params = new URLSearchParams({ scope, domain });
    if (pagePath) params.set("page_path", pagePath);
    return request<Conversation>(`/api/conversations?${params.toString()}`);
  },
  messages: (conversationId: string) =>
    request<{ messages: Message[] }>(`/api/conversations/${conversationId}/messages`),
  jobs: () => request<{ jobs: Job[] }>("/api/jobs"),
  cancelJob: (jobId: string) => request<{ cancelled: boolean }>(`/api/jobs/${jobId}/cancel`, { method: "POST" }),
  startRead: (source: string, domain: string, conversationId?: string, confirmed = false) =>
    request<Job>("/api/jobs/read-paper", {
      method: "POST",
      body: JSON.stringify({ source, domain, conversation_id: conversationId, confirmed })
    }),
  startSurvey: (sources: string[], domain: string, name?: string, conversationId?: string, confirmed = false) =>
    request<Job>("/api/jobs/survey", {
      method: "POST",
      body: JSON.stringify({ sources, domain, name, conversation_id: conversationId, confirmed })
    }),
  startReport: (topic: string, domain: string, papers: string[] = [], conversationId?: string, confirmed = false) =>
    request<Job>("/api/jobs/report", {
      method: "POST",
      body: JSON.stringify({ topic, domain, papers, conversation_id: conversationId, confirmed })
    }),
  startMock: (domain: string, fail = false, conversationId?: string) =>
    request<Job>("/api/jobs/mock", {
      method: "POST",
      body: JSON.stringify({ domain, fail, conversation_id: conversationId })
    })
};

type StreamHandlers = {
  onEvent?: (event: string, data: unknown) => void;
  onChunk?: (text: string) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
};

function parseSsePacket(packet: string): { event: string; data: string } | null {
  const lines = packet.split(/\r?\n/);
  let event = "message";
  const data: string[] = [];
  for (const line of lines) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) data.push(line.slice(5).trimStart());
  }
  if (!data.length) return null;
  return { event, data: data.join("\n") };
}

function decodeData(data: string): unknown {
  try {
    return JSON.parse(data);
  } catch {
    if (data.startsWith("'") && data.endsWith("'")) return data.slice(1, -1);
    return data;
  }
}

export async function streamChat(
  body: { conversation_id: string; page_path?: string; message: string; mode: "page_qa" | "home" | "action" },
  handlers: StreamHandlers
) {
  try {
    const response = await fetch(apiUrl("/api/chat/stream"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!response.ok || !response.body) throw new Error(await response.text());
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const packets = buffer.split(/\n\n/);
      buffer = packets.pop() ?? "";
      for (const packet of packets) {
        const parsed = parseSsePacket(packet);
        if (!parsed) continue;
        const data = decodeData(parsed.data);
        handlers.onEvent?.(parsed.event, data);
        if (parsed.event === "chunk" && typeof data === "object" && data && "text" in data) {
          handlers.onChunk?.(String((data as { text: string }).text));
        }
        if (parsed.event === "done") handlers.onDone?.();
      }
    }
  } catch (error) {
    handlers.onError?.(error instanceof Error ? error : new Error(String(error)));
  }
}

export async function streamJob(jobId: string, handlers: StreamHandlers) {
  try {
    const response = await fetch(apiUrl(`/api/jobs/${jobId}/stream`));
    if (!response.ok || !response.body) throw new Error(await response.text());
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const packets = buffer.split(/\n\n/);
      buffer = packets.pop() ?? "";
      for (const packet of packets) {
        const parsed = parseSsePacket(packet);
        if (!parsed) continue;
        const data = decodeData(parsed.data);
        handlers.onEvent?.(parsed.event, data);
        if (parsed.event === "chunk") handlers.onChunk?.(typeof data === "string" ? data : JSON.stringify(data));
        if (parsed.event === "done") handlers.onDone?.();
      }
    }
  } catch (error) {
    handlers.onError?.(error instanceof Error ? error : new Error(String(error)));
  }
}
