#!/usr/bin/env python3
"""Portable wrapper for document generation.

Loads and runs the implementation at:
  ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py

We intentionally load by file path (not as a package) so the original module's
intra-directory imports (e.g., `from path_parser import ...`) keep working.
"""

from __future__ import annotations

import importlib.util
import os
import sys
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
    return here.parents[2]


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, str(path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    roscoe_root = _get_roscoe_root()
    impl = roscoe_root / "Tools" / "document_generation" / "generate_document.py"

    if not impl.exists():
        raise FileNotFoundError(f"Document generation implementation not found: {impl}")

    mod = _load_module("_roscoe_generate_document", impl)
    # Implementation main() uses argparse + sys.argv.
    mod.main()  # type: ignore
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
