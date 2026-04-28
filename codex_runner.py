from __future__ import annotations

import os
import signal
import shutil
import subprocess
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def codex_available() -> bool:
    return shutil.which("codex") is not None


def run_codex_cli(
    prompt: str,
    *,
    cwd: Path | str = BASE_DIR,
    sandbox: str = "read-only",
    model: str | None = None,
    reasoning_effort: str | None = None,
    timeout: int | None = None,
) -> str:
    """Run the local Codex CLI non-interactively and return its final message."""
    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise RuntimeError("codex CLI is not available on PATH")

    with tempfile.NamedTemporaryFile(prefix="paper-reader-codex-", suffix=".txt", delete=False) as output:
        output_path = Path(output.name)

    command = [codex_bin, "-a", "never"]
    if model:
        command.extend(["-m", model])
    if reasoning_effort:
        command.extend(["-c", f'reasoning_effort="{reasoning_effort}"'])
    command.extend(
        [
            "exec",
            "-s",
            sandbox,
            "-C",
            str(cwd),
            "--output-last-message",
            str(output_path),
            "--color",
            "never",
            "--ephemeral",
            "-",
        ]
    )

    process: subprocess.Popen[str] | None = None
    try:
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            stdout, stderr = process.communicate(input=prompt, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            if process is not None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait(timeout=5)
            detail = f"{int(exc.timeout)} 秒" if exc.timeout else "设定超时"
            raise RuntimeError(
                f"本地 Codex CLI 在 {detail} 内未返回。可调低推理强度，或增大 PAPER_READER_CODEX_TIMEOUT_SECONDS。"
            ) from exc
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        final_message = output_path.read_text(encoding="utf-8", errors="replace").strip() if output_path.exists() else ""
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise RuntimeError(f"codex CLI failed with exit code {result.returncode}: {detail}")
        return final_message or result.stdout.strip()
    finally:
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
