from __future__ import annotations

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

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        final_message = output_path.read_text(encoding="utf-8", errors="replace").strip() if output_path.exists() else ""
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
            raise RuntimeError(f"codex CLI failed with exit code {result.returncode}: {detail}")
        return final_message or result.stdout.strip()
    finally:
        try:
            output_path.unlink()
        except FileNotFoundError:
            pass
