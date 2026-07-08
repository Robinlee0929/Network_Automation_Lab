"""Small file materialization helpers for local report artifacts."""

from __future__ import annotations

import os
from pathlib import Path


def write_text_with_parents(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    """Write text after creating parents, with a Windows long-path fallback."""
    output_path = Path(path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding=encoding)
        return
    except FileNotFoundError:
        if os.name != "nt":
            raise

    extended_path = _windows_extended_path(output_path)
    extended_path.parent.mkdir(parents=True, exist_ok=True)
    extended_path.write_text(content, encoding=encoding)


def read_text_with_long_path(path: Path, *, encoding: str = "utf-8") -> str:
    input_path = Path(path)
    try:
        return input_path.read_text(encoding=encoding)
    except FileNotFoundError:
        if os.name != "nt":
            raise
    return _windows_extended_path(input_path).read_text(encoding=encoding)


def path_exists(path: Path) -> bool:
    input_path = Path(path)
    if input_path.exists():
        return True
    if os.name != "nt":
        return False
    return _windows_extended_path(input_path).exists()


def _windows_extended_path(path: Path) -> Path:
    path_text = str(path.resolve())
    if path_text.startswith("\\\\?\\"):
        return Path(path_text)
    if path_text.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + path_text[2:])
    return Path("\\\\?\\" + path_text)
