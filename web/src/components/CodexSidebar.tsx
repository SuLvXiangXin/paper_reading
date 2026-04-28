import { Bot, FileSearch, HelpCircle, MessageSquare, Route } from "lucide-react";
import { KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

import { api, streamChat } from "../api/client";
import type { ContextBundle, Conversation, Message } from "../api/client";

type Props = {
  domain: string;
  pagePath?: string;
  context?: ContextBundle | null;
};

const quickPrompts = [
  { icon: FileSearch, text: "这篇解决了什么问题，局限是什么?" },
  { icon: MessageSquare, text: "这篇和同方法线代表论文有什么区别?" },
  { icon: Route, text: "如果继续跟进，下一篇该读什么?" },
  { icon: HelpCircle, text: "它在 benchmark 上强在哪里?" }
];

function MessageMarkdown({ content }: { content: string }) {
  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
      {content}
    </ReactMarkdown>
  );
}

export default function CodexSidebar({ domain, pagePath, context }: Props) {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [preparedContext, setPreparedContext] = useState<ContextBundle | null>(null);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [error, setError] = useState("");
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const scope = pagePath ? "page" : "home";
    api
      .conversation(scope, domain, pagePath)
      .then((conv) => {
        setConversation(conv);
        return api.messages(conv.id);
      })
      .then((data) => setMessages(data.messages))
      .catch((err: Error) => setError(err.message));
  }, [domain, pagePath]);

  useEffect(() => {
    if (!pagePath) {
      setPreparedContext(null);
      return;
    }
    api.context(pagePath).then(setPreparedContext).catch(() => setPreparedContext(null));
  }, [pagePath]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, streaming]);

  const activeContext = context ?? preparedContext;
  const contextChanged = useMemo(() => {
    return Boolean(activeContext?.hash && conversation?.context_hash && activeContext.hash !== conversation.context_hash);
  }, [activeContext?.hash, conversation?.context_hash]);

  const send = async (text: string) => {
    if (!conversation || !text.trim() || streaming) return;
    setError("");
    setStatusText("正在准备上下文...");
    setStreaming(true);
    const userMessage: Message = {
      id: Date.now(),
      conversation_id: conversation.id,
      role: "user",
      content: text,
      tool_calls_json: null,
      created_at: new Date().toISOString()
    };
    const assistantId = Date.now() + 1;
    setMessages((prev) => [
      ...prev,
      userMessage,
      {
        id: assistantId,
        conversation_id: conversation.id,
        role: "assistant",
        content: "",
        tool_calls_json: null,
        created_at: new Date().toISOString()
      }
    ]);
    setInput("");
    await streamChat(
      {
        conversation_id: conversation.id,
        page_path: pagePath,
        message: text,
        mode: pagePath ? "page_qa" : "home"
      },
      {
        onEvent(event, data) {
          if (event !== "status") return;
          if (typeof data !== "object" || !data || !("message" in data)) return;
          setStatusText(String((data as { message: unknown }).message));
        },
        onChunk(chunk) {
          setStatusText("");
          setMessages((prev) => prev.map((item) => (item.id === assistantId ? { ...item, content: item.content + chunk } : item)));
        },
        onError(err) {
          setStatusText("");
          setError(err.message);
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId && !item.content ? { ...item, content: `请求失败：${err.message}` } : item
            )
          );
        },
        onDone() {
          setStatusText("");
          setStreaming(false);
        }
      }
    );
    setStreaming(false);
  };

  const insertLineBreak = () => {
    const textarea = inputRef.current;
    if (!textarea) {
      setInput((value) => `${value}\n`);
      return;
    }
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const next = `${input.slice(0, start)}\n${input.slice(end)}`;
    setInput(next);
    window.requestAnimationFrame(() => {
      textarea.selectionStart = start + 1;
      textarea.selectionEnd = start + 1;
    });
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.nativeEvent.isComposing) return;
    if (event.key !== "Enter") return;

    if (event.metaKey || event.ctrlKey) {
      event.preventDefault();
      insertLineBreak();
      return;
    }

    event.preventDefault();
    void send(input);
  };

  return (
    <section className="codex-sidebar">
      <div className="codex-head">
        <div>
          <span className="eyebrow">Codex</span>
          <h2>{pagePath ? "Page Thread" : "Home Thread"}</h2>
        </div>
        <Bot size={19} />
      </div>

      {activeContext && (
        <details className="context-card">
          <summary>
            <span>上下文</span>
            <b>{activeContext.documents.length} files</b>
          </summary>
          <div className="context-top">
            <span>{activeContext.hash}</span>
          </div>
          {contextChanged && <div className="stale-note">文档已更新，历史回答基于旧上下文</div>}
          <div className="context-list">
            {activeContext.documents.slice(0, 8).map((doc) => (
              <div key={`${doc.role}-${doc.path}`} title={doc.path}>
                <b>{doc.role}</b>
                <span>{doc.title}</span>
              </div>
            ))}
          </div>
        </details>
      )}

      {pagePath && activeContext?.page_type === "paper" && (
        <div className="quick-prompts">
          {quickPrompts.map(({ icon: Icon, text }) => (
            <button key={text} onClick={() => void send(text)} disabled={streaming} title={text}>
              <Icon size={14} />
              <span>{text}</span>
            </button>
          ))}
        </div>
      )}

      <div className="message-list" ref={scrollRef}>
        {messages.length === 0 && <div className="empty-thread">尚无历史消息</div>}
        {messages.map((message) => (
          <div className={`message ${message.role}`} key={`${message.id}-${message.created_at}`}>
            <div className="message-role">{message.role === "user" ? "You" : "Codex"}</div>
            <div className="message-content">
              {message.content ? (
                <MessageMarkdown content={message.content} />
              ) : streaming && message.role === "assistant" ? (
                <span className="thinking-status">{statusText || "正在等待响应..."}</span>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      {error && <div className="error-note">{error}</div>}
      <div className="chat-form">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter 发送；Cmd/Ctrl + Enter 换行"
          disabled={streaming || !conversation}
        />
      </div>
    </section>
  );
}
