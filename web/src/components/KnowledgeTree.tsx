import { ChevronDown, FileText, Folder, Home } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { TreeNode } from "../api/client";

type Props = {
  node: TreeNode;
  currentPath: string | null;
  onNavigate: (path: string | null) => void;
};

function labelFor(name: string) {
  return name === "index.md" ? "index" : name.replace(/\.md$/, "");
}

function containsPath(node: TreeNode, path: string | null): boolean {
  if (!path) return false;
  if (node.kind === "document") return node.path === path;
  return node.children.some((child) => containsPath(child, path));
}

function Branch({ node, currentPath, onNavigate, depth = 0 }: Props & { depth?: number }) {
  const hasActiveChild = useMemo(() => containsPath(node, currentPath), [node, currentPath]);
  const [open, setOpen] = useState(depth === 0 || hasActiveChild);

  useEffect(() => {
    if (hasActiveChild) setOpen(true);
  }, [hasActiveChild]);

  if (node.kind === "document") {
    const active = currentPath === node.path;
    return (
      <button
        className={`tree-row doc ${active ? "active" : ""}`}
        style={{ paddingLeft: 12 + depth * 14 }}
        onClick={() => node.path && onNavigate(node.path)}
        title={node.path ?? undefined}
      >
        <FileText size={14} />
        <span>{labelFor(node.name)}</span>
      </button>
    );
  }

  const isRoot = depth === 0;
  return (
    <div className="tree-branch">
      <button
        className={`tree-row dir ${isRoot ? "root" : ""} ${open ? "open" : ""}`}
        style={{ paddingLeft: 12 + depth * 14 }}
        onClick={() => !isRoot && setOpen((value) => !value)}
      >
        {isRoot ? <Home size={14} /> : <Folder size={14} />}
        <span>{node.name}</span>
        {!isRoot && (
          <>
            <small>{node.children.length}</small>
            <ChevronDown className="tree-chevron" size={13} />
          </>
        )}
      </button>
      {open &&
        node.children.map((child) => (
          <Branch
            key={`${child.kind}-${child.path ?? child.name}`}
            node={child}
            currentPath={currentPath}
            onNavigate={onNavigate}
            depth={depth + 1}
          />
        ))}
    </div>
  );
}

export default function KnowledgeTree(props: Props) {
  return <nav className="knowledge-tree"><Branch {...props} /></nav>;
}
