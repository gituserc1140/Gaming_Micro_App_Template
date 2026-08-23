#!/usr/bin/env python3
"""One-click launcher: install deps, start the Flask server, open the browser."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser


PORT = int(os.getenv("PORT", "5000"))
URL = f"http://127.0.0.1:{PORT}"


def _install_deps() -> None:
    req = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print("Installing dependencies…")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "-r", req],
    )


def _open_browser_when_ready(timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=1)  # noqa: S310
            webbrowser.open(URL)
            return
        except (urllib.error.URLError, OSError):
            time.sleep(0.25)


def main() -> None:
    _install_deps()
    threading.Thread(target=_open_browser_when_ready, daemon=True).start()
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Starting server → {URL}  (set HOST=0.0.0.0 for LAN access)")
    # Import here so Flask is available after pip install
    import app as _app  # noqa: PLC0415

    _app.app.run(
        host=host,
        port=PORT,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )


if __name__ == "__main__":
    main()
