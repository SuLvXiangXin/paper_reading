import { BookOpen, FlaskConical, GitBranch, Landmark, Link as LinkIcon } from "lucide-react";

import { appUrl } from "../api/paths";
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

const tagFieldAliases: Record<string, string> = {
  method_tags: "method_tags",
  task_tags: "task_tags",
  component_tags: "component_tags",
  benchmark_tags: "benchmark_tags",
  data_tags: "data_tags",
  robot_tags: "robot_tags",
  application_tags: "application_tags",
  custom_tags: "application_tags",
  tags: "application_tags"
};

function tagKey(facet: string, label: string) {
  const normalized = label
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[/\\]+/g, "-")
    .replace(/[\[\](),;:]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-|-$/g, "");
  return `${facet}:${normalized || label.trim().toLowerCase()}`;
}

function splitTagValues(value: string) {
  const cleaned = value.trim().replace(/^\[/, "").replace(/\]$/, "").replace(/，/g, ",").replace(/；/g, ";");
  return cleaned.split(/\s*[,;]\s*/).map((item) => item.trim().replace(/^["']|["']$/g, "")).filter(Boolean);
}

function explicitTags(content: string) {
  const heading = content.match(/^##\s+标签\s*$/m);
  if (!heading || heading.index === undefined) return [];
  const start = heading.index + heading[0].length;
  const nextHeading = content.slice(start).search(/^##\s+/m);
  const section = nextHeading >= 0 ? content.slice(start, start + nextHeading) : content.slice(start);
  const tags: { facet: string; label: string; key: string }[] = [];
  const seen = new Set<string>();
  for (const line of section.split(/\r?\n/)) {
    const match = line.match(/^\s*-\s*([A-Za-z_]+)\s*[：:]\s*(.+?)\s*$/);
    if (!match) continue;
    const facet = tagFieldAliases[match[1].toLowerCase()];
    if (!facet) continue;
    for (const label of splitTagValues(match[2])) {
      const key = tagKey(facet, label);
      if (seen.has(key)) continue;
      tags.push({ facet, label, key });
      seen.add(key);
    }
  }
  return tags;
}

function openTagFilter(tag: { key: string }) {
  const url = `${appUrl("/")}?paper_tags=${encodeURIComponent(tag.key)}`;
  window.history.pushState({}, "", url);
  window.dispatchEvent(new PopStateEvent("popstate"));
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
  const tags = explicitTags(content).filter((tag) => tag.facet !== "domain").slice(0, 12);

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
      {tags.length > 0 && (
        <div className="paper-tag-strip">
          {tags.map((tag) => (
            <button key={tag.key} onClick={() => openTagFilter(tag)} title={`筛选 ${tag.label}`}>
              {tag.label}
            </button>
          ))}
        </div>
      )}
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
