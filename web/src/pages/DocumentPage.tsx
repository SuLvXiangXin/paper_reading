import { CalendarDays, FileText } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import type { ContextBundle, DocumentResponse } from "../api/client";
import MarkdownViewer from "../components/MarkdownViewer";
import PaperHeader from "../components/PaperHeader";

type Props = {
  path: string;
  onNavigate: (path: string) => void;
};

export default function DocumentPage({ path, onNavigate }: Props) {
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [context, setContext] = useState<ContextBundle | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setDocument(null);
    setContext(null);
    setError("");
    Promise.all([api.document(path), api.context(path)])
      .then(([doc, ctx]) => {
        setDocument(doc);
        setContext(ctx);
      })
      .catch((err: Error) => setError(err.message));
  }, [path]);

  useEffect(() => {
    window.dispatchEvent(new CustomEvent("paper-reader-context", { detail: context }));
  }, [context]);

  if (error) return <div className="page-error">{error}</div>;
  if (!document) return <div className="loading-page">正在读取 Markdown</div>;

  return (
    <div className="document-page">
      <div className="doc-meta">
        <span><FileText size={14} />{document.path}</span>
        <span><CalendarDays size={14} />{new Date(document.updated_at * 1000).toLocaleString()}</span>
      </div>
      {document.page_type === "paper" && (
        <PaperHeader content={document.content} fallbackTitle={document.title} context={context} onNavigate={onNavigate} />
      )}
      {document.page_type !== "paper" && (
        <header className="plain-doc-head">
          <h1>{document.title}</h1>
          <div className="tag-row">
            <span>{document.page_type}</span>
            <span>{document.size} chars</span>
          </div>
        </header>
      )}
      <MarkdownViewer content={document.content} currentPath={document.path} onNavigate={onNavigate} />
    </div>
  );
}
