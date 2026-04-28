from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TreeNode(BaseModel):
    name: str
    path: str | None = None
    kind: Literal["directory", "document"]
    children: list["TreeNode"] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    path: str
    domain: str
    page_type: str
    title: str
    content: str
    updated_at: float
    size: int


class SearchResult(BaseModel):
    path: str
    title: str
    snippet: str
    score: int


class PaperTag(BaseModel):
    facet: str
    label: str
    key: str


class PaperTagOption(PaperTag):
    count: int


class PaperTagFacet(BaseModel):
    facet: str
    label: str
    tags: list[PaperTagOption]


class PaperListItem(BaseModel):
    path: str
    domain: str
    title: str
    year: str | None = None
    summary: str
    method: str | None = None
    tags: list[PaperTag] = Field(default_factory=list)
    updated_at: float


class ContextDocument(BaseModel):
    path: str
    role: str
    title: str
    size: int


class ContextSnippet(BaseModel):
    path: str
    role: str
    title: str
    snippet: str


class ContextBundle(BaseModel):
    page_path: str
    domain: str
    page_type: str
    documents: list[ContextDocument]
    snippets: list[ContextSnippet] = Field(default_factory=list)
    hash: str


class Conversation(BaseModel):
    id: str
    scope: str
    domain: str | None = None
    page_path: str | None = None
    title: str
    context_hash: str | None = None
    created_at: str
    updated_at: str
    archived: bool = False


class Message(BaseModel):
    id: int
    conversation_id: str
    role: str
    content: str
    tool_calls_json: str | None = None
    created_at: str


class ChatRequest(BaseModel):
    session_id: str | None = None
    conversation_id: str
    page_path: str | None = None
    message: str
    mode: Literal["page_qa", "home", "action"] = "page_qa"


class JobRequest(BaseModel):
    domain: str = "vla"
    conversation_id: str | None = None
    confirmed: bool = False


class ReadPaperRequest(JobRequest):
    source: str


class SurveyRequest(JobRequest):
    sources: list[str]
    name: str | None = None


class ReportRequest(JobRequest):
    topic: str
    papers: list[str] = Field(default_factory=list)


class MockJobRequest(JobRequest):
    fail: bool = False


class Job(BaseModel):
    id: str
    conversation_id: str | None = None
    kind: str
    status: str
    command_json: dict[str, Any]
    log_path: str
    created_at: str
    updated_at: str
    return_code: int | None = None


class HomeResponse(BaseModel):
    domain: str
    recent_papers: list[SearchResult]
    recent_reports: list[SearchResult]
    git_status: str
    model: str
    provider_ready: bool
