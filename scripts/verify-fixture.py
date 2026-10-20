#!/usr/bin/env python3
"""Synthetic consumer CI: structural and owner-file regression only.
External GitHub origin, independent digest approval and reviews are NOT verified here.
"""
import json
import pathlib
import re
import hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWNED = {
    "PROJECT.md": "# Synthetic Consumer Project\n\nThis fixture is not a real product.\n",
    "AGENTS.md": "# Synthetic Owner Instructions\n\nProject-owned instructions remain untouched during export adoption.\n",
    "SECURITY.md": "# Synthetic Security Policy\n\nNever publish private identifiers, tokens or source history.\n",
    ".verifier/verifier.config.json": '{"fixture":"consumer-owned configuration; no canonical verifier"}\n',
}
for path, value in OWNED.items():
    assert (ROOT / path).read_bytes() == value.encode("utf-8"), f"owner file modified: {path}"
marker_path = ROOT / "public-safe/adoption.json"
if marker_path.exists():
    data = marker_path.read_bytes()
    marker = json.loads(data)
    assert set(marker) == {
        "schemaVersion", "profile", "profileVersion", "exportId",
        "publicManifestDigest", "publicationCommit",
    }
    assert marker["schemaVersion"] == marker["profileVersion"] == 2
    assert marker["profile"] == "loop-public-safe-governance"
    for name in ("exportId", "publicManifestDigest"):
        assert re.fullmatch(r"[0-9a-f]{64}", marker[name])
    assert re.fullmatch(r"[0-9a-f]{40}", marker["publicationCommit"])
    assert data == (json.dumps(marker, separators=(",", ":")) + "\n").encode()
    for name in ("engineering-review.md", "security-review.md"):
        p = ROOT / "governance" / name
        contents = p.read_bytes()
        assert 0 < len(contents) <= 16384
        assert all(c in (9, 10) or 32 <= c <= 126 for c in contents)
        assert not re.search(rb"ghp_[a-zA-Z0-9]{10}|github_pat_|-----BEGIN", contents)
print("SYNTHETIC_CONSUMER_CI=PASS (structure only; external approval not checked)")
