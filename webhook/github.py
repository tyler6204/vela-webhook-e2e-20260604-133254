"""GitHub-specific authentication, decoding, normalization, and policy."""

from typing import Mapping, Optional, Union

from .models import NormalizedEvent, PolicyDecision, TriggerPolicy

SecretValue = Union[str, bytes]


def verify_signature(
    payload_body: bytes,
    secrets: Mapping[str, SecretValue],
    signature_header: Optional[str],
) -> str:
    """Return the ID of the secret matching a canonical GitHub SHA-256 signature."""
    raise NotImplementedError


def decode_payload(payload_body: bytes) -> dict:
    """Decode one strict UTF-8 JSON object with no duplicate keys or non-finite numbers."""
    raise NotImplementedError


def normalize_event(event_type: str, payload: dict, delivery_id: str) -> NormalizedEvent:
    """Normalize a supported GitHub event into the stable CI trigger model."""
    raise NotImplementedError


def evaluate_policy(event: NormalizedEvent, policy: TriggerPolicy) -> PolicyDecision:
    """Return a deterministic accept/reject decision for a normalized event."""
    raise NotImplementedError
