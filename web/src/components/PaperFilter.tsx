import { BookMarked, Filter, Search, X } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import type { PaperListItem, PaperTagFacet } from "../api/client";

type Props = {
  domain: string;
  onNavigate: (path: string) => void;
};

function readInitialTags() {
  const params = new URLSearchParams(window.location.search);
  const tags = params.get("paper_tags");
  return tags ? tags.split(",").filter(Boolean) : params.getAll("paper_tag").filter(Boolean);
}

function readInitialQuery() {
  return new URLSearchParams(window.location.search).get("paper_q") ?? "";
}

function writeUrlState(tags: string[], query: string) {
  const params = new URLSearchParams(window.location.search);
  if (tags.length) params.set("paper_tags", tags.join(","));
  else params.delete("paper_tags");
  params.delete("paper_tag");
  if (query.trim()) params.set("paper_q", query.trim());
  else params.delete("paper_q");
  const next = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}`;
  window.history.replaceState({}, "", next);
}

function tagLabel(path: string) {
  return path.split("/").slice(1).join("/");
}

export default function PaperFilter({ domain, onNavigate }: Props) {
  const [facets, setFacets] = useState<PaperTagFacet[]>([]);
  const [papers, setPapers] = useState<PaperListItem[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>(() => readInitialTags());
  const [query, setQuery] = useState(() => readInitialQuery());
  const [error, setError] = useState("");

  useEffect(() => {
    api.paperTags(domain).then((data) => setFacets(data.facets)).catch((err: Error) => setError(err.message));
  }, [domain]);

  useEffect(() => {
    setError("");
    writeUrlState(selectedTags, query);
    api
      .papers({ domain, query, tags: selectedTags })
      .then((data) => setPapers(data.papers))
      .catch((err: Error) => setError(err.message));
  }, [domain, query, selectedTags]);

  const toggleTag = (key: string) => {
    setSelectedTags((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));
  };

  const clear = () => {
    setSelectedTags([]);
    setQuery("");
  };

  const hasFilter = selectedTags.length > 0 || query.trim().length > 0;

  return (
    <section className="paper-filter-panel">
      <div className="section-head">
        <div>
          <span className="eyebrow">Paper Filter</span>
          <h2>按标签筛选论文</h2>
        </div>
        <Filter size={18} />
      </div>

      <div className="filter-search">
        <Search size={16} />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="在筛选结果中搜索 title / tag / summary"
        />
        {hasFilter && (
          <button onClick={clear} title="清除筛选">
            <X size={14} />
            <span>清除</span>
          </button>
        )}
      </div>

      <div className="facet-stack">
        {facets
          .filter((facet) => facet.facet !== "domain")
          .map((facet) => (
            <div className="facet-group" key={facet.facet}>
              <div className="facet-label">{facet.label}</div>
              <div className="tag-chip-row">
                {facet.tags.slice(0, 18).map((tag) => (
                  <button
                    key={tag.key}
                    className={`tag-chip ${selectedTags.includes(tag.key) ? "active" : ""}`}
                    onClick={() => toggleTag(tag.key)}
                    title={`${tag.label} (${tag.count})`}
                  >
                    <span>{tag.label}</span>
                    <b>{tag.count}</b>
                  </button>
                ))}
              </div>
            </div>
          ))}
      </div>

      <div className="filter-result-head">
        <span>{papers.length} 篇匹配</span>
        <small>同类标签为 OR，不同类别为 AND</small>
      </div>

      <div className="paper-filter-results">
        {papers.slice(0, 24).map((paper) => (
          <button key={paper.path} className="paper-result-card" onClick={() => onNavigate(paper.path)}>
            <div>
              <BookMarked size={15} />
              <strong>{paper.title}</strong>
            </div>
            <span>{tagLabel(paper.path)}</span>
            <small>{paper.summary || paper.method || "暂无摘要"}</small>
            <div className="mini-tag-row">
              {paper.tags
                .filter((tag) => tag.facet !== "domain")
                .slice(0, 5)
                .map((tag) => (
                  <em key={tag.key}>{tag.label}</em>
                ))}
            </div>
          </button>
        ))}
      </div>

      {papers.length > 24 && <div className="filter-more">仅显示前 24 篇，继续缩小标签或关键词可精确定位。</div>}
      {error && <div className="error-note">{error}</div>}
    </section>
  );
}
