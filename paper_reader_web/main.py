from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import db, jobs
from .chat import chat_stream, provider_ready
from .config import BASE_DIR, CODEX_MODEL, DEFAULT_DOMAIN, WEB_DIST_DIR
from .context import prepare_context
from .documents import build_tree, list_domains, read_document, recent_documents, search_knowledge
from .schemas import ChatRequest, MockJobRequest, ReadPaperRequest, ReportRequest, SurveyRequest
from .security import normalize_kb_path, validate_domain


app = FastAPI(title="Paper Reader Web", version="0.1.0")

_PROXY_PREFIX_RE = re.compile(r"^(?P<prefix>/(?:.+/)?proxy/\d+)(?P<rest>/.*)?$")


@app.middleware("http")
async def _strip_notebook_proxy_prefix(request, call_next):
    path = request.scope.get("path", "")
    request.scope["paper_reader_original_path"] = path
    match = _PROXY_PREFIX_RE.match(path)
    if match:
        request.scope["path"] = match.group("rest") or "/"
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "model": CODEX_MODEL or "codex default", "provider_ready": provider_ready(), "repo": str(BASE_DIR)}


@app.get("/api/domains")
def domains() -> dict[str, list[str]]:
    return {"domains": list_domains()}


@app.get("/api/tree")
def tree(domain: str = DEFAULT_DOMAIN):
    return build_tree(domain)


@app.get("/api/document")
def document(path: str):
    return read_document(path)


@app.get("/api/search")
def search(q: str = Query(..., min_length=1), domain: str | None = None):
    return {"results": search_knowledge(q, domain=domain)}


@app.get("/api/context/prepare")
def context_prepare(path: str):
    return prepare_context(path)


@app.get("/api/conversations")
def conversation(scope: str = "page", domain: str | None = None, page_path: str | None = None):
    if scope == "page":
        if not page_path:
            raise HTTPException(status_code=400, detail="page_path is required for page conversations")
        normalized = normalize_kb_path(page_path)
        context = prepare_context(normalized)
        title = read_document(normalized).title
        return db.get_or_create_conversation(
            scope="page",
            domain=context.domain,
            page_path=normalized,
            title=title,
            context_hash=context.hash,
        )
    domain = validate_domain(domain or DEFAULT_DOMAIN)
    return db.get_or_create_conversation(scope=scope, domain=domain, page_path=None, title=f"{domain} home")


@app.get("/api/conversations/{conversation_id}/messages")
def messages(conversation_id: str):
    if not db.get_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"messages": db.list_messages(conversation_id)}


@app.post("/api/chat/stream")
def chat(request: ChatRequest):
    return StreamingResponse(chat_stream(request), media_type="text/event-stream")


@app.get("/api/git/status")
def git_status() -> dict[str, str]:
    result = subprocess.run(["git", "status", "--short"], cwd=BASE_DIR, capture_output=True, text=True)
    return {"status": result.stdout.strip(), "return_code": str(result.returncode)}


def _require_job_confirmation(confirmed: bool) -> None:
    if not confirmed:
        raise HTTPException(status_code=409, detail="This job can modify the knowledge base and requires confirmation.")


@app.get("/api/home")
def home(domain: str = DEFAULT_DOMAIN):
    domain = validate_domain(domain)
    status = git_status()["status"]
    return {
        "domain": domain,
        "recent_papers": recent_documents(domain, "papers", limit=8),
        "recent_reports": recent_documents(domain, "reports", limit=5),
        "git_status": status,
        "model": CODEX_MODEL or "codex default",
        "provider_ready": provider_ready(),
    }


@app.post("/api/jobs/read-paper")
def read_paper_job(request: ReadPaperRequest):
    domain = validate_domain(request.domain)
    _require_job_confirmation(request.confirmed)
    return jobs.start_read_job(request.source, domain, request.conversation_id)


@app.post("/api/jobs/survey")
def survey_job(request: SurveyRequest):
    domain = validate_domain(request.domain)
    _require_job_confirmation(request.confirmed)
    if not request.sources:
        raise HTTPException(status_code=400, detail="sources is required")
    return jobs.start_survey_job(request.sources, domain, request.name, request.conversation_id)


@app.post("/api/jobs/report")
def report_job(request: ReportRequest):
    domain = validate_domain(request.domain)
    _require_job_confirmation(request.confirmed)
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="topic is required")
    return jobs.start_report_job(request.topic, domain, request.papers, request.conversation_id)


@app.post("/api/jobs/mock")
def mock_job(request: MockJobRequest):
    domain = validate_domain(request.domain)
    return jobs.start_mock_job(domain, request.fail, request.conversation_id)


@app.get("/api/jobs")
def list_jobs():
    return {"jobs": db.list_jobs()}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    if not db.get_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"cancelled": jobs.cancel_job(job_id)}


@app.get("/api/jobs/{job_id}/stream")
async def job_stream(job_id: str):
    async def stream():
        offset = 0
        while True:
            job = db.get_job(job_id)
            if not job:
                yield f"event: error\ndata: {{\"message\":\"Job not found\"}}\n\n"
                return
            chunk, offset = jobs.read_log(job, offset)
            if chunk:
                yield f"event: chunk\ndata: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            if job.status in {"succeeded", "failed", "cancelled"}:
                yield f"event: done\ndata: {job.model_dump_json()}\n\n"
                return
            await asyncio.sleep(0.5)

    return StreamingResponse(stream(), media_type="text/event-stream")


if WEB_DIST_DIR.exists():
    assets_dir = WEB_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


def _index_file() -> Path:
    index = WEB_DIST_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Frontend has not been built. Run npm run build in web/.")
    return index


def _asset_prefix(request: Request) -> str:
    original_path = str(request.scope.get("paper_reader_original_path") or request.scope.get("path") or "")
    match = _PROXY_PREFIX_RE.match(original_path)
    return match.group("prefix") if match else ""


def _index_response(request: Request) -> HTMLResponse:
    html = _index_file().read_text(encoding="utf-8")
    asset_prefix = _asset_prefix(request)
    if asset_prefix:
        asset_base = f"{asset_prefix}/assets/"
        html = html.replace('src="./assets/', f'src="{asset_base}')
        html = html.replace('href="./assets/', f'href="{asset_base}')
    else:
        html = _dynamic_asset_index(html)
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})


def _dynamic_asset_index(html: str) -> str:
    script_match = re.search(r'<script[^>]+src="(\./assets/[^"]+)"[^>]*></script>', html)
    style_match = re.search(r'<link[^>]+href="(\./assets/[^"]+)"[^>]*>', html)
    if not script_match or not style_match:
        return html
    script_src = script_match.group(1).removeprefix(".")
    style_href = style_match.group(1).removeprefix(".")
    loader = f"""<script>
      (() => {{
        const match = window.location.pathname.match(/^(.*\\/proxy\\/\\d+)(?:\\/.*)?$/);
        const base = match ? match[1] : "";
        const style = document.createElement("link");
        style.rel = "stylesheet";
        style.crossOrigin = "";
        style.href = `${{base}}{style_href}`;
        document.head.appendChild(style);
        const script = document.createElement("script");
        script.type = "module";
        script.crossOrigin = "";
        script.src = `${{base}}{script_src}`;
        document.head.appendChild(script);
      }})();
    </script>"""
    html = re.sub(r'\s*<script[^>]+src="\./assets/[^"]+"[^>]*></script>', "", html)
    html = re.sub(r'\s*<link[^>]+href="\./assets/[^"]+"[^>]*>', "", html)
    return html.replace("</head>", f"{loader}\n  </head>")


@app.get("/")
def frontend_root(request: Request):
    return _index_response(request)


@app.get("/docs/{doc_path:path}")
def frontend_doc(doc_path: str, request: Request):
    return _index_response(request)


@app.get("/{full_path:path}")
def frontend_fallback(full_path: str, request: Request):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    return _index_response(request)
