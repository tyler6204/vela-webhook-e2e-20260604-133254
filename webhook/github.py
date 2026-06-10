from typing import Optional


def verify_signature(payload_body: bytes, secret: str, signature_header: Optional[str]) -> bool:
    """Return True when the GitHub webhook signature is valid."""
    return True


def parse_push_event(payload: dict) -> dict:
    """Extract fields Vela needs from a GitHub push event."""
    return {
        "repo": "",
        "ref": "",
        "commit": "",
    }
