from __future__ import annotations

import json
import re
from typing import Any, Iterable

from codex_runner import codex_available, run_codex_cli

from . import db
from .config import BASE_DIR, WEB_CODEX_MODEL, WEB_CODEX_REASONING_EFFORT, WEB_CODEX_TIMEOUT_SECONDS
from .context import prepare_context
from .schemas import ChatRequest, ContextBundle
from .security import safe_read_text


DOC_PROMPT_LIMITS = {
    "current_page": 7000,
    "current_paper": 7000,
    "domain_overview": 1400,
    "papers_index": 1400,
    "explicit_link": 1000,
    "method_line": 1800,
    "component": 1200,
    "task": 800,
    "benchmark": 1000,
    "neighbor_paper": 1200,
}


def _sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _chunk_text(text: str, size: int = 64) -> Iterable[str]:
    for i in range(0, len(text), size):
        yield text[i : i + size]


def provider_ready() -> bool:
    return codex_available()


def _trim_text(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 18)].rstrip() + "\n\n[truncated]"


def _provided_context(bundle: ContextBundle) -> str:
    blocks: list[str] = []
    for doc in bundle.documents:
        limit = DOC_PROMPT_LIMITS.get(doc.role, 900)
        try:
            content = safe_read_text(doc.path)
        except Exception:
            continue
        blocks.append(
            "\n".join(
                [
                    f"### {doc.role}: knowledge_base/{doc.path}",
                    f"Title: {doc.title}",
                    "```markdown",
                    _trim_text(content, limit),
                    "```",
                ]
            )
        )
    if bundle.snippets:
        snippet_lines = ["### related_snippets"]
        for snip in bundle.snippets[:6]:
            snippet_lines.append(
                f"- knowledge_base/{snip.path} ({snip.role}, {snip.title}): {_trim_text(snip.snippet, 420)}"
            )
        blocks.append("\n".join(snippet_lines))
    return "\n\n".join(blocks) or "No inline context available."


def _system_prompt(bundle: ContextBundle, mode: str) -> str:
    context_lines = "\n".join(
        f"- knowledge_base/{doc.path} ({doc.role}, {doc.title}, {doc.size} chars)" for doc in bundle.documents
    )
    provided_context = _provided_context(bundle)
    action_rule = (
        "This is read-only page QA. Do not write files or claim that files were modified."
        if mode != "action"
        else "Actions must be proposed first; do not claim a write happened unless the web app starts a confirmed job."
    )
    return f"""You are the Codex sidebar for a local paper-reading knowledge base.

Answer in Chinese unless the user asks otherwise. Be concise, comparative, and cite concrete Markdown paths when useful.
You are running through the local `codex exec` CLI in a read-only sandbox for page QA.

Current page: knowledge_base/{bundle.page_path}
Domain: {bundle.domain}
Page type: {bundle.page_type}
Context hash: {bundle.hash}

Available context manifest:
{context_lines or "- none"}

Provided document contents and excerpts:
{provided_context}

Rules:
- Use the provided current page and excerpts first. For most page QA, answer directly from them.
- Only inspect additional repository files if the provided context is clearly insufficient.
- For comparisons, prefer the supplied related paper/method excerpts before doing new search.
- {action_rule}
- If the knowledge base is insufficient, say what is missing instead of inventing details.
"""


def _history_text(conversation_id: str, *, exclude_message_id: int | None = None) -> str:
    rows = db.list_messages(conversation_id, limit=16)
    if not rows:
        return "- none"
    lines = []
    for row in rows:
        if exclude_message_id is not None and row.id == exclude_message_id:
            continue
        if row.role not in {"user", "assistant"}:
            continue
        lines.append(f"{row.role}: {row.content}")
    return "\n\n".join(lines) or "- none"


def _fallback_answer(request: ChatRequest, bundle: ContextBundle) -> str:
    current = safe_read_text(bundle.page_path)[:3000] if request.page_path else ""
    title = ""
    match = re.search(r"^#\s+(.+)", current, re.MULTILINE)
    if match:
        title = match.group(1)
    method = re.search(r"方法线归属\*{0,2}\s*[：:]\s*(.+)", current)
    idea = re.search(r"核心\s*idea\*{0,2}\s*[：:]\s*(.+)", current, re.IGNORECASE)
    benchmark = re.search(r"Benchmark\*{0,2}\s*[：:]\s*(.+)", current, re.IGNORECASE)
    summary = re.search(r"##\s+一句话总结\s+([\s\S]*?)(?:\n##\s+|$)", current)
    paths = "\n".join(f"- `knowledge_base/{doc.path}` ({doc.role})" for doc in bundle.documents[:6])
    extracted = []
    if method:
        extracted.append(f"- 方法线: {method.group(1).strip()}")
    if idea:
        extracted.append(f"- 核心 idea: {idea.group(1).strip()}")
    if benchmark:
        extracted.append(f"- Benchmark: {benchmark.group(1).strip()}")
    if summary:
        extracted.append(f"- 一句话总结: {summary.group(1).strip()[:260]}")
    extracted_text = f"从当前页直接抽取到:\n{chr(10).join(extracted)}\n\n" if extracted else ""
    return (
        "当前后端没有检测到本地 `codex` CLI，所以这次使用本地只读回退回答。\n\n"
        f"当前页: `knowledge_base/{bundle.page_path}` {title}\n\n"
        f"{extracted_text}"
        f"已准备上下文:\n{paths}\n\n"
        "服务端已保存这条对话历史；安装并登录 Codex CLI 后，同一个侧边栏会通过本地 `codex exec` 回答。"
    )


def run_chat(
    request: ChatRequest,
    bundle: ContextBundle,
    *,
    exclude_history_message_id: int | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    if not provider_ready():
        return _fallback_answer(request, bundle), []

    prompt = f"""{_system_prompt(bundle, request.mode)}

Conversation history:
{_history_text(request.conversation_id, exclude_message_id=exclude_history_message_id)}

Latest user message:
{request.message}

Return only the assistant answer. Do not include tool logs or execution traces.
"""
    answer = run_codex_cli(
        prompt,
        cwd=BASE_DIR,
        sandbox="read-only",
        model=WEB_CODEX_MODEL or None,
        reasoning_effort=WEB_CODEX_REASONING_EFFORT or None,
        timeout=WEB_CODEX_TIMEOUT_SECONDS,
    )
    return answer.strip() or "Codex CLI 没有返回文本。", []


def chat_stream(request: ChatRequest) -> Iterable[str]:
    conversation = db.get_conversation(request.conversation_id)
    if not conversation:
        yield _sse("error", {"message": "Conversation not found"})
        return

    page_path = request.page_path or conversation.page_path
    if not page_path:
        page_path = f"{conversation.domain or 'vla'}/index.md"
    yield _sse("status", {"message": "正在准备知识库上下文..."})
    bundle = prepare_context(page_path)
    user_message = db.add_message(request.conversation_id, "user", request.message)
    db.touch_conversation(request.conversation_id, context_hash=bundle.hash)

    yield _sse("meta", {"context_hash": bundle.hash, "documents": [doc.model_dump() for doc in bundle.documents]})
    effort = WEB_CODEX_REASONING_EFFORT or "default"
    yield _sse(
        "status",
        {
            "message": (
                f"已准备 {len(bundle.documents)} 份上下文，正在调用本地 Codex CLI "
                f"（reasoning: {effort}, timeout: {WEB_CODEX_TIMEOUT_SECONDS}s）..."
            )
        },
    )
    try:
        answer, tool_events = run_chat(request, bundle, exclude_history_message_id=user_message.id)
    except Exception as exc:
        answer = f"Codex CLI 调用失败: {exc}"
        tool_events = []
    if tool_events:
        yield _sse("tools", tool_events)
    for chunk in _chunk_text(answer):
        yield _sse("chunk", {"text": chunk})
    db.add_message(request.conversation_id, "assistant", answer, tool_events)
    yield _sse("done", {"message": "ok"})
