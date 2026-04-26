import { Search } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client";
import type { SearchResult } from "../api/client";

type Props = {
  onNavigate: (path: string) => void;
};

function resultDomain(path: string) {
  return path.split("/", 1)[0] || "global";
}

export default function SearchBox({ onNavigate }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const handle = window.setTimeout(() => {
      api.search(query).then((data) => {
        setResults(data.results);
        setOpen(true);
      });
    }, 180);
    return () => window.clearTimeout(handle);
  }, [query]);

  return (
    <div className="search-box">
      <Search size={16} />
      <input
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        onFocus={() => setOpen(true)}
        placeholder="全局搜索论文、方法、benchmark"
      />
      {open && results.length > 0 && (
        <div className="search-popover">
          {results.map((item) => (
            <button
              key={item.path}
              onClick={() => {
                onNavigate(item.path);
                setOpen(false);
                setQuery("");
              }}
            >
              <strong><span>{resultDomain(item.path)}</span>{item.title}</strong>
              <span>{item.path}</span>
              <small>{item.snippet}</small>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
