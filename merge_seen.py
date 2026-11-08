#!/usr/bin/env python3
"""Sloučí dvě verze seen.json z rebase konfliktu (stage 2 a stage 3).

Používá se v GitHub Actions, když souběžný běh mezitím commitnul seen.json.
Výsledkem je sjednocení podle (source, id), aby se neztratily ani jedny ID.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def read_stage(stage: int) -> list[dict]:
    result = subprocess.run(
        ["git", "show", f":{stage}:seen.json"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def key(item: dict) -> tuple[str, str]:
    source = item.get("source")
    if not source:
        link = item.get("link") or item.get("url") or ""
        source = "bezrealitky" if "bezrealitky" in link else "sreality"
    return source, str(item.get("id"))


def main() -> None:
    merged: dict[tuple[str, str], dict] = {}
    for stage in (2, 3):
        for item in read_stage(stage):
            if isinstance(item, dict):
                merged[key(item)] = item

    Path("seen.json").write_text(
        json.dumps(list(merged.values())[-5000:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
