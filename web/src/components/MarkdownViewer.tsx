import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

import MermaidBlock from "./MermaidBlock";

type Props = {
  content: string;
  currentPath: string;
  onNavigate: (path: string) => void;
};

function resolveHref(currentPath: string, href: string): string | null {
  if (!href || href.startsWith("#") || /^[a-zA-Z]+:/.test(href)) return null;
  const [pathPart, hash] = href.split("#");
  if (!pathPart.endsWith(".md")) return null;
  let cleanPath = pathPart.replace(/^\/+/, "");
  if (cleanPath.startsWith("knowledge_base/")) cleanPath = cleanPath.slice("knowledge_base/".length);
  const currentParts = currentPath.split("/");
  currentParts.pop();
  const isAbsolute = href.startsWith("/") || cleanPath.split("/")[0] === currentPath.split("/")[0];
  const base = isAbsolute ? [] : currentParts;
  const parts = [...base, ...cleanPath.split("/")].filter(Boolean);
  const stack: string[] = [];
  for (const part of parts) {
    if (part === ".") continue;
    if (part === "..") stack.pop();
    else stack.push(part);
  }
  return `${stack.join("/")}${hash ? `#${hash}` : ""}`;
}

export default function MarkdownViewer({ content, currentPath, onNavigate }: Props) {
  return (
    <article className="markdown-body">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          a({ href, children, ...props }) {
            const target = href ? resolveHref(currentPath, href) : null;
            if (target) {
              return (
                <button className="markdown-link" onClick={() => onNavigate(target.split("#")[0])}>
                  {children}
                </button>
              );
            }
            return (
              <a href={href} target={href?.startsWith("http") ? "_blank" : undefined} rel="noreferrer" {...props}>
                {children}
              </a>
            );
          },
          code({ className, children, ...props }) {
            const language = /language-(\w+)/.exec(className ?? "")?.[1];
            const code = String(children).replace(/\n$/, "");
            if (language === "mermaid") return <MermaidBlock chart={code} />;
            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          table({ children }) {
            return (
              <div className="table-wrap">
                <table>{children}</table>
              </div>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </article>
  );
}
