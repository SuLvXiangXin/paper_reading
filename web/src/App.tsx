import { useEffect, useMemo, useState } from "react";
import { Menu, MessageSquareText } from "lucide-react";

import { api } from "./api/client";
import type { TreeNode } from "./api/client";
import { appUrl, stripPublicBasePath } from "./api/paths";
import KnowledgeTree from "./components/KnowledgeTree";
import SearchBox from "./components/SearchBox";
import CodexSidebar from "./components/CodexSidebar";
import DocumentPage from "./pages/DocumentPage";
import HomePage from "./pages/HomePage";

function routeToPath(): string | null {
  const pathname = decodeURI(stripPublicBasePath(window.location.pathname));
  if (pathname.startsWith("/docs/")) return pathname.slice("/docs/".length);
  return null;
}

export default function App() {
  const [domains, setDomains] = useState<string[]>([]);
  const [domain, setDomain] = useState("vla");
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [currentPath, setCurrentPath] = useState<string | null>(() => routeToPath());
  const [navOpen, setNavOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    api.domains().then((data) => {
      setDomains(data.domains);
      if (!data.domains.includes(domain) && data.domains[0]) setDomain(data.domains[0]);
    });
  }, []);

  useEffect(() => {
    if (currentPath) {
      const nextDomain = currentPath.split("/")[0];
      if (nextDomain && nextDomain !== domain) setDomain(nextDomain);
    }
  }, [currentPath, domain]);

  useEffect(() => {
    api.tree(domain).then(setTree).catch(() => setTree(null));
  }, [domain]);

  useEffect(() => {
    const onPop = () => setCurrentPath(routeToPath());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = (path: string | null) => {
    setCurrentPath(path);
    const url = path ? appUrl(`/docs/${path}`) : appUrl("/");
    window.history.pushState({}, "", url);
    setNavOpen(false);
  };

  const switchDomain = (nextDomain: string) => {
    setDomain(nextDomain);
    navigate(`${nextDomain}/index.md`);
  };

  const sidebarContext = useMemo(() => {
    return currentPath ? { scope: "page" as const, pagePath: currentPath } : { scope: "home" as const };
  }, [currentPath]);

  const pathLabel = currentPath ?? `${domain}/home`;

  return (
    <div className={`app-shell ${navOpen ? "nav-open" : ""} ${chatOpen ? "chat-open" : ""}`}>
      <header className="topbar">
        <button className="icon-button mobile-only" title="目录" onClick={() => setNavOpen((open) => !open)}>
          <Menu size={18} />
        </button>
        <button className="brand" onClick={() => navigate(null)}>
          <span className="brand-mark">PR</span>
          <span>Paper Reader</span>
        </button>
        <select value={domain} onChange={(event) => switchDomain(event.target.value)} aria-label="领域">
          {domains.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <SearchBox onNavigate={navigate} />
        <div className="topbar-context" title={pathLabel}>
          <span className="domain-chip">{domain}</span>
          <span className="path-chip">{pathLabel}</span>
        </div>
        <button className="icon-button mobile-only" title="对话" onClick={() => setChatOpen((open) => !open)}>
          <MessageSquareText size={18} />
        </button>
      </header>

      <aside className="nav-panel">
        <div className="panel-title">Knowledge Base</div>
        {tree ? <KnowledgeTree node={tree} currentPath={currentPath} onNavigate={navigate} /> : <div className="muted">目录加载中</div>}
      </aside>

      <main className="content-panel">
        {currentPath ? (
          <DocumentPage path={currentPath} onNavigate={navigate} />
        ) : (
          <HomePage domain={domain} onNavigate={navigate} />
        )}
      </main>

      <aside className="codex-panel">
        <CodexSidebar domain={domain} pagePath={sidebarContext.scope === "page" ? sidebarContext.pagePath : undefined} />
      </aside>
      <div className="mobile-backdrop" onClick={() => { setNavOpen(false); setChatOpen(false); }} />
    </div>
  );
}
