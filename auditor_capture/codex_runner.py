from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_MODELS = {"gpt-5.4", "gpt-5.5"}


@dataclass(frozen=True)
class CodexConfig:
    binary: str = "codex"
    skip_git_repo_check: bool = True
    ephemeral: bool = True
    ignore_user_config: bool = True
    ignore_rules: bool = True
    sandbox: str = "read-only"
    cwd: Path = Path(".")


def build_codex_command(
    *,
    model: str,
    output_last_message: Path,
    output_schema: Path | None,
    config: CodexConfig,
) -> list[str]:
    if model not in ALLOWED_MODELS:
        raise ValueError(f"Model {model!r} is not allowed; use one of {sorted(ALLOWED_MODELS)}")

    command = [config.binary, "exec", "-m", model, "-C", str(config.cwd)]
    if config.skip_git_repo_check:
        command.append("--skip-git-repo-check")
    if config.ephemeral:
        command.append("--ephemeral")
    if config.ignore_user_config:
        command.append("--ignore-user-config")
    if config.ignore_rules:
        command.append("--ignore-rules")
    if config.sandbox:
        command.extend(["--sandbox", config.sandbox])
    if output_schema:
        command.extend(["--output-schema", str(output_schema)])
    command.extend(["-o", str(output_last_message), "-"])
    return command


def run_codex_json(
    *,
    prompt: str,
    model: str,
    output_last_message: Path,
    output_schema: Path | None,
    config: CodexConfig,
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    output_last_message.parent.mkdir(parents=True, exist_ok=True)
    command = build_codex_command(
        model=model,
        output_last_message=output_last_message,
        output_schema=output_schema,
        config=config,
    )
    completed = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "codex exec failed\n"
            f"command={command!r}\n"
            f"stdout={completed.stdout}\n"
            f"stderr={completed.stderr}"
        )
    try:
        return json.loads(output_last_message.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Codex output was not valid JSON in {output_last_message}: {exc}\n"
            f"raw={output_last_message.read_text(encoding='utf-8')}"
        ) from exc

