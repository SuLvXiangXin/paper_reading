from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterable

from .config import STATE_DB
from .schemas import Conversation, Job, Message
from .security import ensure_state_dirs


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect() -> Iterable[sqlite3.Connection]:
    ensure_state_dirs()
    conn = sqlite3.connect(STATE_DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            create table if not exists conversations(
              id text primary key,
              scope text not null,
              domain text,
              page_path text,
              title text not null,
              context_hash text,
              created_at text not null,
              updated_at text not null,
              archived integer not null default 0
            );

            create table if not exists messages(
              id integer primary key autoincrement,
              conversation_id text not null,
              role text not null,
              content text not null,
              tool_calls_json text,
              created_at text not null,
              foreign key(conversation_id) references conversations(id)
            );

            create table if not exists conversation_summaries(
              conversation_id text not null,
              upto_message_id integer not null,
              summary text not null,
              created_at text not null,
              context_hash text
            );

            create table if not exists jobs(
              id text primary key,
              conversation_id text,
              kind text not null,
              status text not null,
              command_json text not null,
              log_path text not null,
              created_at text not null,
              updated_at text not null,
              return_code integer
            );

            create index if not exists idx_conversations_scope_page
              on conversations(scope, domain, page_path, archived, updated_at);
            create index if not exists idx_messages_conversation
              on messages(conversation_id, id);
            create index if not exists idx_jobs_updated
              on jobs(updated_at);
            """
        )


def _conversation_from_row(row: sqlite3.Row) -> Conversation:
    return Conversation(
        id=row["id"],
        scope=row["scope"],
        domain=row["domain"],
        page_path=row["page_path"],
        title=row["title"],
        context_hash=row["context_hash"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        archived=bool(row["archived"]),
    )


def get_or_create_conversation(
    *,
    scope: str,
    domain: str | None,
    page_path: str | None,
    title: str,
    context_hash: str | None = None,
) -> Conversation:
    init_db()
    with connect() as conn:
        if scope == "page":
            row = conn.execute(
                """
                select * from conversations
                where scope = ? and page_path = ? and archived = 0
                order by updated_at desc limit 1
                """,
                (scope, page_path),
            ).fetchone()
        else:
            row = conn.execute(
                """
                select * from conversations
                where scope = ? and coalesce(domain, '') = coalesce(?, '') and archived = 0
                order by updated_at desc limit 1
                """,
                (scope, domain),
            ).fetchone()
        if row:
            if context_hash and not row["context_hash"]:
                conn.execute(
                    "update conversations set context_hash = ?, updated_at = ? where id = ?",
                    (context_hash, utc_now(), row["id"]),
                )
                row = conn.execute("select * from conversations where id = ?", (row["id"],)).fetchone()
            return _conversation_from_row(row)

        now = utc_now()
        conversation_id = str(uuid.uuid4())
        conn.execute(
            """
            insert into conversations(id, scope, domain, page_path, title, context_hash, created_at, updated_at, archived)
            values (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (conversation_id, scope, domain, page_path, title, context_hash, now, now),
        )
        row = conn.execute("select * from conversations where id = ?", (conversation_id,)).fetchone()
        return _conversation_from_row(row)


def get_conversation(conversation_id: str) -> Conversation | None:
    init_db()
    with connect() as conn:
        row = conn.execute("select * from conversations where id = ?", (conversation_id,)).fetchone()
        return _conversation_from_row(row) if row else None


def touch_conversation(conversation_id: str, *, context_hash: str | None = None) -> None:
    with connect() as conn:
        if context_hash:
            conn.execute(
                "update conversations set updated_at = ?, context_hash = ? where id = ?",
                (utc_now(), context_hash, conversation_id),
            )
        else:
            conn.execute("update conversations set updated_at = ? where id = ?", (utc_now(), conversation_id))


def add_message(conversation_id: str, role: str, content: str, tool_calls: Any | None = None) -> Message:
    now = utc_now()
    tool_json = json.dumps(tool_calls, ensure_ascii=False) if tool_calls is not None else None
    with connect() as conn:
        cursor = conn.execute(
            """
            insert into messages(conversation_id, role, content, tool_calls_json, created_at)
            values (?, ?, ?, ?, ?)
            """,
            (conversation_id, role, content, tool_json, now),
        )
        conn.execute("update conversations set updated_at = ? where id = ?", (now, conversation_id))
        row = conn.execute("select * from messages where id = ?", (cursor.lastrowid,)).fetchone()
        return Message(
            id=row["id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            tool_calls_json=row["tool_calls_json"],
            created_at=row["created_at"],
        )


def list_messages(conversation_id: str, limit: int | None = None) -> list[Message]:
    init_db()
    query = "select * from messages where conversation_id = ? order by id"
    args: tuple[Any, ...] = (conversation_id,)
    if limit is not None:
        query = "select * from (select * from messages where conversation_id = ? order by id desc limit ?) order by id"
        args = (conversation_id, limit)
    with connect() as conn:
        rows = conn.execute(query, args).fetchall()
        return [
            Message(
                id=row["id"],
                conversation_id=row["conversation_id"],
                role=row["role"],
                content=row["content"],
                tool_calls_json=row["tool_calls_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]


def _job_from_row(row: sqlite3.Row) -> Job:
    return Job(
        id=row["id"],
        conversation_id=row["conversation_id"],
        kind=row["kind"],
        status=row["status"],
        command_json=json.loads(row["command_json"]),
        log_path=row["log_path"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        return_code=row["return_code"],
    )


def create_job(kind: str, command: dict[str, Any], log_path: str, conversation_id: str | None = None) -> Job:
    now = utc_now()
    job_id = str(uuid.uuid4())
    with connect() as conn:
        conn.execute(
            """
            insert into jobs(id, conversation_id, kind, status, command_json, log_path, created_at, updated_at)
            values (?, ?, ?, 'queued', ?, ?, ?, ?)
            """,
            (job_id, conversation_id, kind, json.dumps(command, ensure_ascii=False), log_path, now, now),
        )
        row = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
        return _job_from_row(row)


def update_job(job_id: str, *, status: str | None = None, return_code: int | None = None) -> None:
    parts = ["updated_at = ?"]
    args: list[Any] = [utc_now()]
    if status is not None:
        parts.append("status = ?")
        args.append(status)
    if return_code is not None:
        parts.append("return_code = ?")
        args.append(return_code)
    args.append(job_id)
    with connect() as conn:
        conn.execute(f"update jobs set {', '.join(parts)} where id = ?", args)


def get_job(job_id: str) -> Job | None:
    init_db()
    with connect() as conn:
        row = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
        return _job_from_row(row) if row else None


def list_jobs(limit: int = 30) -> list[Job]:
    init_db()
    with connect() as conn:
        rows = conn.execute("select * from jobs order by updated_at desc limit ?", (limit,)).fetchall()
        return [_job_from_row(row) for row in rows]
