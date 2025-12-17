#!/usr/bin/env python3
"""Wrapper that exposes create_case() from workflows/tools/create_case.py (portable)."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType


def _get_roscoe_root() -> Path:
    env = os.environ.get("ROSCOE_ROOT")
    if env:
        return Path(env)

    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "workflow_engine").exists() and (p / "workflows").exists():
            return p
    return here.parents[5]


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, str(path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_roscoe_root = _get_roscoe_root()
_impl = _load_module("_roscoe_create_case", _roscoe_root / "workflows" / "tools" / "create_case.py")

create_case = _impl.create_case  # type: ignore

__all__ = ["create_case"]
