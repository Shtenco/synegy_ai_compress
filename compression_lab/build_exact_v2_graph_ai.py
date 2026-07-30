#!/usr/bin/env python3
"""Build the graph-AI edition from the exact user-provided v2 source.

Usage:
    python build_exact_v2_graph_ai.py /path/to/egd256_web_app_v2.py \
        --output egd256_web_app_v5_graph_ai.py
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

MARKER = "# For development\nif __name__ == '__main__':"
PATCH = '''# SHTENCO GRAPH-AI V5 integration: original source above is preserved.\nfrom graph_ai_v2_integration import install_graph_ai\nGRAPH_AI_MANIFEST = install_graph_ai(globals())\n\n# For development\nif __name__ == '__main__':'''


def build(source_path: Path, output_path: Path) -> dict:
    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        raise ValueError("exact v2 development marker was not found")
    if "GRAPH_AI_MANIFEST = install_graph_ai" in source:
        patched = source
    else:
        patched = source.replace(MARKER, PATCH, 1)
    patched = patched.replace("SHTENCO EGD-256 ARCHIVER v3.0", "SHTENCO EGD-256 GRAPH-AI ARCHIVER v5.0", 1)
    output_path.write_text(patched, encoding="utf-8")
    return {
        "source": str(source_path),
        "output": str(output_path),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "output_sha256": hashlib.sha256(patched.encode("utf-8")).hexdigest(),
        "source_bytes": len(source.encode("utf-8")),
        "output_bytes": len(patched.encode("utf-8")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("egd256_web_app_v5_graph_ai.py"))
    args = parser.parse_args()
    print(build(args.source, args.output))


if __name__ == "__main__":
    main()
