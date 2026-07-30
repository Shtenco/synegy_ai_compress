#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SHTENCO EGD-256 GRAPH-AI ARCHIVER v5 launcher.

Keep this file beside the exact user-provided ``egd256_web_app_v2.py`` and all
of its original dependency modules. The original module is imported, patched
in its own namespace, and then exported unchanged as the Flask application.
"""
from __future__ import annotations
import threading
import webbrowser

import egd256_web_app_v2 as original
from graph_ai_v2_integration import install_graph_ai

GRAPH_AI_MANIFEST = install_graph_ai(vars(original))
app = original.app
application = original.application
create_app = original.create_app
AdvancedArchiver = original.AdvancedArchiver


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║       SHTENCO EGD-256 GRAPH-AI ARCHIVER V5 — 42 ENGINES      ║")
    print("║       Exact v2 Matrix UI + all proprietary graph engines      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(GRAPH_AI_MANIFEST)
    threading.Timer(1.5, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False, threaded=True)
