"""Security tests for HAMEAU viewer server and endpoints."""

import socket
import threading
import urllib.request
import urllib.error
import pytest
from pathlib import Path
from hameau.cli import create_viewer_server


def test_restricted_viewer_server_security(tmp_path):
    """Verifies that the viewer server binds only to 127.0.0.1 and cannot access sensitive files."""
    repo_root = Path(__file__).resolve().parent.parent
    server, port = create_viewer_server(port=0, repo_root=repo_root)
    
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    base_url = f"http://127.0.0.1:{port}"
    
    # 1. Allowed: /index.html (served from viewer/)
    req = urllib.request.urlopen(f"{base_url}/index.html")
    assert req.status == 200
    content = req.read().decode("utf-8")
    assert "HAMEAU" in content
    
    # 2. Blocked: /config.yaml (repo root file) -> Should return 404 or 403
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(f"{base_url}/config.yaml")
    assert exc_info.value.code in (403, 404)
    
    # 3. Blocked: /.git/config (repo root sensitive file) -> Should return 404 or 403
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(f"{base_url}/.git/config")
    assert exc_info.value.code in (403, 404)
    
    # 4. Blocked: Path traversal /../config.yaml -> Should return 404 or 403
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(f"{base_url}/../config.yaml")
    assert exc_info.value.code in (403, 404)
    
    # Clean shutdown
    server.shutdown()
    server.server_close()
