import hashlib
import hmac
import json
from pathlib import Path

from webhook.github import parse_push_event, verify_signature

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "push.json"
SECRET = "test-webhook-secret"


def sign_payload(payload_body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_verify_signature_accepts_valid_header():
    body = b'{"ref":"refs/heads/main"}'
    header = sign_payload(body, SECRET)
    assert verify_signature(body, SECRET, header) is True


def test_verify_signature_rejects_invalid_header():
    body = b'{"ref":"refs/heads/main"}'
    assert verify_signature(body, SECRET, "sha256=deadbeef") is False


def test_verify_signature_rejects_missing_header():
    body = b'{"ref":"refs/heads/main"}'
    assert verify_signature(body, SECRET, None) is False


def test_parse_push_event_extracts_vela_fields():
    payload = json.loads(FIXTURE_PATH.read_text())
    parsed = parse_push_event(payload)
    assert parsed == {
        "repo": "vela-org/demo-repo",
        "ref": "refs/heads/main",
        "commit": "abc123def4567890",
    }
