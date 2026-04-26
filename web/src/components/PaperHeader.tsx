import { BookOpen, FlaskConical, GitBranch, Landmark, Link as LinkIcon } from "lucide-react";

import type { ContextBundle } from "../api/client";

function field(content: string, names: string[]) {
  for (const name of names) {
    const match = content.match(new RegExp(`(?:-\\s*)?(?:\\*{0,2}${name}\\*{0,2})\\s*[：:]\\s*(.+)`, "i"));
    if (match) return match[1].replace(/\*\*/g, "").trim();
  }
  return "";
}

function title(content: string, fallback: string) {
  return content.match(/^#\s+(.+)$/m)?.[1].trim() ?? fallback;
}

type Props = {
  content: string;
  fallbackTitle: string;
  context: ContextBundle | null;
  onNavigate: (path: string) => void;
};

export default function PaperHeader({ content, fallbackTitle, context, onNavigate }: Props) {
  const method = field(content, ["方法线归属", "方法线"]);
  const arxiv = field(content, ["arXiv", "链接"]);
  const org = field(content, ["机构"]);
  const benchmark = field(content, ["Benchmark", "Benchmarks"]);
  const summary = content.match(/##\s+一句话总结\s+([\s\S]*?)(?:\n##\s+|$)/)?.[1]?.trim();
  const related = context?.documents.filter((doc) => ["method_line", "benchmark", "neighbor_paper"].includes(doc.role)).slice(0, 5) ?? [];

  return (
    <section className="paper-header">
      <div className="paper-heading">
        <BookOpen size={20} />
        <h1>{title(content, fallbackTitle)}</h1>
      </div>
      {summary && <p className="paper-summary">{summary}</p>}
      <div className="tag-row">
        {method && <span><GitBranch size={13} />{method}</span>}
        {benchmark && <span><FlaskConical size={13} />{benchmark}</span>}
        {org && <span><Landmark size={13} />{org}</span>}
        {arxiv && <span><LinkIcon size={13} />{arxiv}</span>}
      </div>
      {related.length > 0 && (
        <div className="related-strip">
          {related.map((doc) => (
            <button key={doc.path} onClick={() => onNavigate(doc.path)} title={doc.path}>
              {doc.role === "neighbor_paper" ? "相邻" : doc.role} · {doc.title}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
