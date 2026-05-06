"""Compatibility adapter for the legacy top-level MCP server module."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from types import ModuleType


def _ensure_import_paths() -> None:
    """Ensure both the project root and scripts/ are on sys.path."""
    root = Path(__file__).resolve().parents[2]
    root_str = str(root)
    scripts_str = str(root / "scripts")
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)


def get_legacy_module() -> ModuleType:
    _ensure_import_paths()
    try:
        return import_module("mcp_server")
    except ModuleNotFoundError as exc:
        if getattr(exc, "name", None) != "mcp_server":
            raise
        raise RuntimeError(
            "Cannot locate the legacy mcp_server module. Ensure the scholar-agent package is installed correctly."
        ) from None


def main() -> int:
    result = get_legacy_module().main()
    return 0 if result is None else int(result)
