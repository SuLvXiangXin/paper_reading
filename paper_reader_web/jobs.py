from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from . import db
from .config import BASE_DIR, CONDA_ENV, JOB_LOG_DIR
from .schemas import Job
from .security import ensure_state_dirs


_processes: dict[str, subprocess.Popen[str]] = {}
_lock = threading.Lock()


def _new_log_path(kind: str, job_id: str) -> Path:
    ensure_state_dirs()
    return JOB_LOG_DIR / f"{kind}_{job_id}.log"


def _paper_reader_command(args: list[str]) -> list[str]:
    return ["conda", "run", "-n", CONDA_ENV, "python", "paper_reader.py", *args]


def start_command_job(kind: str, command: list[str], conversation_id: str | None = None) -> Job:
    temp_id = "pending"
    log_path = _new_log_path(kind, temp_id)
    job = db.create_job(kind, {"argv": command}, str(log_path.relative_to(BASE_DIR)), conversation_id)
    real_log_path = _new_log_path(kind, job.id)
    log_path.rename(real_log_path) if log_path.exists() else None
    with db.connect() as conn:
        conn.execute(
            "update jobs set log_path = ?, command_json = ? where id = ?",
            (str(real_log_path.relative_to(BASE_DIR)), json.dumps({"argv": command}, ensure_ascii=False), job.id),
        )
    job = db.get_job(job.id)
    thread = threading.Thread(target=_run_subprocess, args=(job.id, command, real_log_path), daemon=True)
    thread.start()
    return job


def start_read_job(source: str, domain: str, conversation_id: str | None = None) -> Job:
    return start_command_job(
        "read",
        _paper_reader_command(["read", source, "--domain", domain, "--no-sync"]),
        conversation_id,
    )


def start_survey_job(sources: list[str], domain: str, name: str | None, conversation_id: str | None = None) -> Job:
    args = ["survey", *sources, "--domain", domain]
    if name:
        args.extend(["--name", name])
    return start_command_job("survey", _paper_reader_command(args), conversation_id)


def start_report_job(topic: str, domain: str, papers: list[str], conversation_id: str | None = None) -> Job:
    args = ["report", topic, "--domain", domain]
    if papers:
        args.extend(["--papers", *papers])
    return start_command_job("report", _paper_reader_command(args), conversation_id)


def start_mock_job(domain: str, fail: bool = False, conversation_id: str | None = None) -> Job:
    job = db.create_job("mock", {"domain": domain, "fail": fail}, "", conversation_id)
    log_path = _new_log_path("mock", job.id)
    with db.connect() as conn:
        conn.execute("update jobs set log_path = ? where id = ?", (str(log_path.relative_to(BASE_DIR)), job.id))
    thread = threading.Thread(target=_run_mock, args=(job.id, log_path, fail), daemon=True)
    thread.start()
    return db.get_job(job.id)


def _run_subprocess(job_id: str, command: list[str], log_path: Path) -> None:
    db.update_job(job_id, status="running")
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.flush()
        try:
            process = subprocess.Popen(
                command,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                start_new_session=True,
            )
            with _lock:
                _processes[job_id] = process
            assert process.stdout is not None
            for line in process.stdout:
                log.write(line)
                log.flush()
            return_code = process.wait()
            current = db.get_job(job_id)
            if current and current.status == "cancelled":
                return
            if return_code in {-signal.SIGTERM, -signal.SIGKILL}:
                db.update_job(job_id, status="cancelled", return_code=return_code)
                return
            status = "succeeded" if return_code == 0 else "failed"
            db.update_job(job_id, status=status, return_code=return_code)
        except Exception as exc:
            log.write(f"\n[web job error] {exc}\n")
            db.update_job(job_id, status="failed", return_code=-1)
        finally:
            with _lock:
                _processes.pop(job_id, None)


def _run_mock(job_id: str, log_path: Path, fail: bool) -> None:
    db.update_job(job_id, status="running")
    with log_path.open("w", encoding="utf-8") as log:
        for step in range(1, 5):
            log.write(f"[mock] step {step}/4\n")
            log.flush()
            time.sleep(0.35)
        if fail:
            log.write("[mock] intentional failure\n")
            db.update_job(job_id, status="failed", return_code=1)
        else:
            log.write("[mock] completed\n")
            db.update_job(job_id, status="succeeded", return_code=0)


def cancel_job(job_id: str) -> bool:
    with _lock:
        process = _processes.get(job_id)
    if not process:
        return False
    db.update_job(job_id, status="cancelled", return_code=-signal.SIGTERM)
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except Exception:
        process.terminate()
    return True


def read_log(job: Job, start: int = 0) -> tuple[str, int]:
    log_path = BASE_DIR / job.log_path
    if not log_path.exists():
        return "", start
    data = log_path.read_text(encoding="utf-8", errors="replace")
    return data[start:], len(data)
