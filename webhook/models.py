"""Stable public data models used by the webhook processor."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class NormalizedEvent:
    event: str
    delivery_id: str
    repository: str
    action: str
    ref: str
    sha: Optional[str]
    sender: str
    installation_id: Optional[int]
    before: Optional[str] = None
    base_ref: Optional[str] = None
    base_sha: Optional[str] = None
    number: Optional[int] = None
    commits: Tuple[str, ...] = ()
    changed_files: Tuple[str, ...] = ()
    messages: Tuple[str, ...] = ()
    forced: bool = False
    deleted: bool = False
    fork: bool = False
    draft: bool = False
    skip_ci: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    accepted: bool
    reason: str


@dataclass(frozen=True)
class DeliveryResult:
    delivery_id: str
    signature_key_id: str
    event: NormalizedEvent
    decision: PolicyDecision
    duplicate: bool = False


@dataclass(frozen=True)
class TriggerPolicy:
    allowed_events: Tuple[str, ...] = ("push", "pull_request", "merge_group")
    allowed_repositories: Tuple[str, ...] = ("*",)
    allowed_refs: Tuple[str, ...] = ("refs/heads/*", "refs/tags/*", "refs/pull/*")
    ignored_refs: Tuple[str, ...] = ()
    blocked_senders: Tuple[str, ...] = ()
    allow_fork_pull_requests: bool = False
    skip_ci_tokens: Tuple[str, ...] = ("[skip ci]", "[ci skip]")
    max_payload_bytes: int = 1_048_576
    replay_ttl_seconds: float = 86_400.0
    replay_capacity: int = 10_000
