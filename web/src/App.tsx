import { useEffect, useMemo, useState } from "react";
import type { CSSProperties, PointerEvent as ReactPointerEvent } from "react";
import { Menu, MessageSquareText } from "lucide-react";

import { api } from "./api/client";
import type { TreeNode } from "./api/client";
import { appUrl, stripPublicBasePath } from "./api/paths";
import KnowledgeTree from "./components/KnowledgeTree";
import SearchBox from "./components/SearchBox";
import CodexSidebar from "./components/CodexSidebar";
import DocumentPage from "./pages/DocumentPage";
import HomePage from "./pages/HomePage";

const LEFT_WIDTH_KEY = "paper-reader:left-sidebar-width";
const RIGHT_WIDTH_KEY = "paper-reader:right-sidebar-width";
const LEFT_MIN = 240;
const LEFT_MAX = 560;
const RIGHT_MIN = 360;
const RIGHT_MAX = 860;
const CONTENT_MIN = 360;
const RESIZER_TOTAL_WIDTH = 20;

function routeToPath(): string | null {
  const pathname = decodeURI(stripPublicBasePath(window.location.pathname));
  if (pathname.startsWith("/docs/")) return pathname.slice("/docs/".length);
  return null;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function storedWidth(key: string, fallback: number, min: number, max: number) {
  const value = Number(window.localStorage.getItem(key));
  return Number.isFinite(value) ? clamp(value, min, max) : fallback;
}

function defaultLeftWidth() {
  if (window.innerWidth <= 1320) return 300;
  return 330;
}

function defaultRightWidth() {
  if (window.innerWidth <= 1320) return Math.max(420, Math.round(window.innerWidth * 0.32));
  return Math.max(480, Math.round(window.innerWidth * 0.34));
}

export default function App() {
  const [domains, setDomains] = useState<string[]>([]);
  const [domain, setDomain] = useState("vla");
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [currentPath, setCurrentPath] = useState<string | null>(() => routeToPath());
  const [navOpen, setNavOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(() =>
    storedWidth(LEFT_WIDTH_KEY, defaultLeftWidth(), LEFT_MIN, LEFT_MAX)
  );
  const [rightSidebarWidth, setRightSidebarWidth] = useState(() =>
    storedWidth(RIGHT_WIDTH_KEY, defaultRightWidth(), RIGHT_MIN, RIGHT_MAX)
  );

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
    const fitWidthsToViewport = () => {
      if (window.matchMedia("(max-width: 1120px)").matches) return;
      const available = window.innerWidth - CONTENT_MIN - RESIZER_TOTAL_WIDTH;
      let nextLeft = clamp(leftSidebarWidth, LEFT_MIN, LEFT_MAX);
      let nextRight = clamp(rightSidebarWidth, RIGHT_MIN, RIGHT_MAX);
      if (nextLeft + nextRight > available) {
        nextRight = clamp(available - nextLeft, RIGHT_MIN, RIGHT_MAX);
        if (nextLeft + nextRight > available) {
          nextLeft = clamp(available - nextRight, LEFT_MIN, LEFT_MAX);
        }
      }
      if (nextLeft !== leftSidebarWidth) {
        setLeftSidebarWidth(nextLeft);
        window.localStorage.setItem(LEFT_WIDTH_KEY, String(Math.round(nextLeft)));
      }
      if (nextRight !== rightSidebarWidth) {
        setRightSidebarWidth(nextRight);
        window.localStorage.setItem(RIGHT_WIDTH_KEY, String(Math.round(nextRight)));
      }
    };

    fitWidthsToViewport();
    window.addEventListener("resize", fitWidthsToViewport);
    return () => window.removeEventListener("resize", fitWidthsToViewport);
  }, [leftSidebarWidth, rightSidebarWidth]);

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

  const startSidebarResize = (side: "left" | "right") => (event: ReactPointerEvent<HTMLDivElement>) => {
    if (window.matchMedia("(max-width: 1120px)").matches) return;
    event.preventDefault();
    const target = event.currentTarget;
    target.setPointerCapture(event.pointerId);
    document.body.classList.add("is-resizing-sidebar");

    const onPointerMove = (moveEvent: PointerEvent) => {
      const viewportWidth = window.innerWidth;
      if (side === "left") {
        const maxLeft = Math.min(LEFT_MAX, viewportWidth - rightSidebarWidth - CONTENT_MIN - RESIZER_TOTAL_WIDTH);
        const next = clamp(moveEvent.clientX, LEFT_MIN, Math.max(LEFT_MIN, maxLeft));
        setLeftSidebarWidth(next);
        window.localStorage.setItem(LEFT_WIDTH_KEY, String(Math.round(next)));
      } else {
        const maxRight = Math.min(RIGHT_MAX, viewportWidth - leftSidebarWidth - CONTENT_MIN - RESIZER_TOTAL_WIDTH);
        const next = clamp(viewportWidth - moveEvent.clientX, RIGHT_MIN, Math.max(RIGHT_MIN, maxRight));
        setRightSidebarWidth(next);
        window.localStorage.setItem(RIGHT_WIDTH_KEY, String(Math.round(next)));
      }
    };

    const stopResize = () => {
      document.body.classList.remove("is-resizing-sidebar");
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", stopResize);
      window.removeEventListener("pointercancel", stopResize);
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", stopResize);
    window.addEventListener("pointercancel", stopResize);
  };

  const pathLabel = currentPath ?? `${domain}/home`;

  return (
    <div
      className={`app-shell ${navOpen ? "nav-open" : ""} ${chatOpen ? "chat-open" : ""}`}
      style={
        {
          "--left-sidebar-width": `${leftSidebarWidth}px`,
          "--right-sidebar-width": `${rightSidebarWidth}px`
        } as CSSProperties
      }
    >
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

      <div
        className="sidebar-resizer sidebar-resizer-left"
        role="separator"
        aria-label="调整左侧栏宽度"
        aria-orientation="vertical"
        onPointerDown={startSidebarResize("left")}
      />

      <main className="content-panel">
        {currentPath ? (
          <DocumentPage path={currentPath} onNavigate={navigate} />
        ) : (
          <HomePage domain={domain} onNavigate={navigate} />
        )}
      </main>

      <div
        className="sidebar-resizer sidebar-resizer-right"
        role="separator"
        aria-label="调整右侧栏宽度"
        aria-orientation="vertical"
        onPointerDown={startSidebarResize("right")}
      />

      <aside className="codex-panel">
        <CodexSidebar domain={domain} pagePath={sidebarContext.scope === "page" ? sidebarContext.pagePath : undefined} />
      </aside>
      <div className="mobile-backdrop" onClick={() => { setNavOpen(false); setChatOpen(false); }} />
    </div>
  );
}
