"""Start isolated local servers, run the browser workflow, then stop owned processes."""

import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def ready(url, process):
    for _ in range(150):
        if process.poll() is not None:
            raise RuntimeError("A test server exited. See artifacts/e2e-servers.log")
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except OSError:
            time.sleep(0.2)
    raise RuntimeError("A test server did not become ready")


def main():
    api_port, web_port = free_port(), free_port()
    api_url, web_url = f"http://127.0.0.1:{api_port}", f"http://127.0.0.1:{web_port}"
    environment = {
        **os.environ,
        "SIXTH_E2E": "1",
        "PYTHONPATH": str(ROOT / "tests"),
        "SIXTH_MEMORY_BACKEND": "sqlite_fixture",
        "SIXTH_DATA_DIR": str(ROOT / "data" / ("e2e-" + uuid4().hex)),
        "SIXTH_MODEL_API_KEY": "",
        "SIXTH_MODEL_NAME": "",
        "SIXTH_DEMO_LOGIN": "true",
        "SIXTH_COOKIE_SECURE": "false",
        "SIXTH_ALLOWED_ORIGINS": json.dumps([web_url]),
        "SIXTH_API_URL": api_url,
        "SIXTH_WEB_URL": web_url,
    }
    processes = []
    (ROOT / "artifacts").mkdir(exist_ok=True)
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    with (ROOT / "artifacts/e2e-servers.log").open("w", encoding="utf-8") as log:
        try:
            api = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "browser_app:app",
                    "--app-dir",
                    "apps/api",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(api_port),
                ],
                cwd=ROOT,
                env=environment,
                stdout=log,
                stderr=log,
                creationflags=flags,
            )
            processes.append(api)
            ready(api_url + "/health/live", api)
            web = subprocess.Popen(
                [
                    "node",
                    str(ROOT / "node_modules/vite/bin/vite.js"),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(web_port),
                ],
                cwd=ROOT / "apps/web",
                env=environment,
                stdout=log,
                stderr=log,
                creationflags=flags,
            )
            processes.append(web)
            ready(web_url, web)
            return subprocess.call(
                [sys.executable, "-m", "pytest", "tests/test_browser.py", "-q"], cwd=ROOT, env=environment
            )
        finally:
            for process in reversed(processes):
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
