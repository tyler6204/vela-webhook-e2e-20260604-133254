import hashlib
import hmac
import json
from pathlib import Path

import pytest

from webhook.errors import (
    DeliveryInProgress,
    InvalidSignature,
    MalformedPayload,
    MalformedSignature,
    ReplayConflict,
)
from webhook.github import decode_payload, evaluate_policy, normalize_event, verify_signature
from webhook.models import TriggerPolicy
from webhook.processor import WebhookProcessor
from webhook.replay import ReplayCache

FIXTURES = Path(__file__).parent / "fixtures"
SECRETS = {"old": "retiring-secret", "current": "current-secret"}
DELIVERY_ID = "0f47d4ac-0e9b-4f4f-b9d7-18f5867c2501"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def encoded_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def sign(body: bytes, secret: str = "current-secret") -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def headers(event: str, body: bytes, **overrides: str) -> dict:
    values = {
        "Content-Type": "application/json; charset=utf-8",
        "X-GitHub-Event": event,
        "X-GitHub-Delivery": DELIVERY_ID,
        "X-Hub-Signature-256": sign(body),
    }
    values.update(overrides)
    return values


def test_signature_rotation_returns_matching_key_id():
    body = b'{"zen":"keep it logically awesome"}'
    assert verify_signature(body, SECRETS, sign(body, "retiring-secret")) == "old"
    assert verify_signature(body, SECRETS, sign(body)) == "current"


@pytest.mark.parametrize(
    "header",
    [
        None,
        "",
        "sha1=" + ("0" * 40),
        "sha256=deadbeef",
        "sha256=" + ("G" * 64),
        " sha256=" + ("0" * 64),
    ],
)
def test_signature_header_is_canonical(header):
    body = b"{}"
    error = MalformedSignature if header is not None else Exception
    with pytest.raises(error):
        verify_signature(body, SECRETS, header)


def test_validly_formed_but_wrong_signature_is_rejected():
    with pytest.raises(InvalidSignature):
        verify_signature(b"{}", SECRETS, "sha256=" + ("0" * 64))


@pytest.mark.parametrize(
    "body",
    [
        b'{"a":1,"a":2}',
        b'{"value":NaN}',
        b'["not", "an", "object"]',
        b"\xff",
    ],
)
def test_decode_payload_rejects_ambiguous_or_invalid_json(body):
    with pytest.raises(MalformedPayload):
        decode_payload(body)


def test_push_normalization_collects_commits_and_changed_files():
    event = normalize_event("push", fixture("push.json"), DELIVERY_ID)
    assert event.repository == "vela-org/demo-repo"
    assert event.action == "updated"
    assert event.ref == "refs/heads/main"
    assert event.sha == "2222222222222222222222222222222222222222"
    assert event.commits == (
        "2222222222222222222222222222222222222222",
        "3333333333333333333333333333333333333333",
    )
    assert event.changed_files == (
        "tests/legacy.py",
        "tests/test_github_webhook.py",
        "webhook/github.py",
        "webhook/processor.py",
    )


def test_pull_request_normalization_detects_same_repo_head():
    event = normalize_event("pull_request", fixture("pull_request.json"), DELIVERY_ID)
    assert event.action == "synchronize"
    assert event.number == 42
    assert event.ref == "refs/pull/42/head"
    assert event.base_ref == "refs/heads/main"
    assert event.fork is False


def test_merge_group_normalization_uses_queue_ref():
    event = normalize_event("merge_group", fixture("merge_group.json"), DELIVERY_ID)
    assert event.action == "checks_requested"
    assert event.ref == "refs/heads/gh-readonly-queue/main/pr-42-deadbeef"
    assert event.base_ref == "refs/heads/main"


def test_policy_applies_repository_ref_sender_and_skip_ci_rules():
    event = normalize_event("push", fixture("push.json"), DELIVERY_ID)
    policy = TriggerPolicy(
        allowed_repositories=("vela-org/*",),
        allowed_refs=("refs/heads/main",),
    )
    assert evaluate_policy(event, policy).accepted is True
    assert evaluate_policy(
        event,
        TriggerPolicy(blocked_senders=("OCTOCAT",)),
    ).reason == "blocked_sender"

    skipped = fixture("push.json")
    skipped["head_commit"]["message"] = "docs only [skip ci]"
    skipped_event = normalize_event("push", skipped, DELIVERY_ID)
    assert evaluate_policy(skipped_event, policy).reason == "skip_ci"


def test_replay_cache_distinguishes_duplicate_conflict_and_in_progress():
    now = [100.0]
    cache = ReplayCache(ttl_seconds=60, capacity=2, clock=lambda: now[0])
    reservation = cache.reserve(DELIVERY_ID, "fingerprint-a")

    with pytest.raises(DeliveryInProgress):
        cache.reserve(DELIVERY_ID, "fingerprint-a")
    with pytest.raises(ReplayConflict):
        cache.reserve(DELIVERY_ID, "fingerprint-b")

    result = object()
    cache.commit(reservation, result)
    duplicate = cache.reserve(DELIVERY_ID, "fingerprint-a")
    assert duplicate.duplicate is True
    assert duplicate.result is result


def test_replay_abort_and_expiry_allow_retry():
    now = [100.0]
    cache = ReplayCache(ttl_seconds=10, capacity=1, clock=lambda: now[0])
    first = cache.reserve(DELIVERY_ID, "fingerprint")
    cache.abort(first)
    second = cache.reserve(DELIVERY_ID, "fingerprint")
    cache.commit(second, "done")

    now[0] += 11
    third = cache.reserve(DELIVERY_ID, "fingerprint")
    assert third.duplicate is False


def test_processor_runs_the_full_pipeline_and_caches_result():
    body = encoded_fixture("push.json")
    processor = WebhookProcessor(
        SECRETS,
        TriggerPolicy(
            allowed_repositories=("vela-org/*",),
            allowed_refs=("refs/heads/main",),
        ),
    )

    result = processor.process(headers("push", body), body)
    duplicate = processor.process(headers("push", body), body)

    assert result.signature_key_id == "current"
    assert result.decision.accepted is True
    assert result.duplicate is False
    assert duplicate.duplicate is True
    assert duplicate.event == result.event


def test_processor_verifies_the_exact_raw_body():
    body = encoded_fixture("push.json")
    reformatted = json.dumps(json.loads(body)).encode()
    processor = WebhookProcessor(SECRETS)

    with pytest.raises(InvalidSignature):
        processor.process(headers("push", body), reformatted)
