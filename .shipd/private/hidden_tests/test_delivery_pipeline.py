import copy
import hashlib
import hmac
import json
import threading
from pathlib import Path

import pytest

from webhook.errors import (
    DeliveryInProgress,
    InvalidSignature,
    MalformedHeaders,
    MalformedPayload,
    MalformedSignature,
    PayloadTooLarge,
    ReplayCapacityExceeded,
    ReplayConflict,
    UnsupportedEvent,
    UnsupportedMediaType,
)
from webhook.github import decode_payload, evaluate_policy, normalize_event, verify_signature
from webhook.models import DeliveryResult, TriggerPolicy
from webhook.processor import WebhookProcessor
from webhook.replay import ReplayCache

FIXTURES = Path("tests/fixtures")
DELIVERY_A = "53e844f5-b2bf-48d3-a24f-79d64c12f08a"
DELIVERY_B = "27c570d8-fe3b-42c2-b94a-fde2534dc796"
DELIVERY_C = "e730e04f-b6cc-4738-bc4e-57d8e214f5ce"
SECRETS = {
    "retired": b"retired-secret",
    "current": "current-secret",
    "next": "next-secret",
}
ZERO_SHA = "0" * 40


def load_fixture(name):
    return json.loads((FIXTURES / name).read_text())


def encode(payload):
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()


def sign(body, secret="current-secret"):
    digest = hmac.new(
        secret.encode() if isinstance(secret, str) else secret,
        body,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def request_headers(event, body, delivery_id=DELIVERY_A, **overrides):
    headers = {
        "content-type": "application/json",
        "x-github-event": event,
        "x-github-delivery": delivery_id,
        "x-hub-signature-256": sign(body),
    }
    headers.update(overrides)
    return headers


def test_signature_checks_every_configured_secret(monkeypatch):
    body = b'{"delivery":"rotation"}'
    calls = []
    original = hmac.compare_digest

    def recording_compare(left, right):
        calls.append((left, right))
        return original(left, right)

    monkeypatch.setattr("webhook.github.hmac.compare_digest", recording_compare)
    assert verify_signature(body, SECRETS, sign(body, b"retired-secret")) == "retired"
    assert len(calls) == len(SECRETS)


@pytest.mark.parametrize(
    "secrets",
    [
        {},
        {"": "secret"},
        {"id": ""},
        {"id": object()},
    ],
)
def test_signature_rejects_invalid_secret_configuration(secrets):
    with pytest.raises((TypeError, ValueError)):
        verify_signature(b"{}", secrets, "sha256=" + ("0" * 64))


@pytest.mark.parametrize(
    "header",
    [
        "SHA256=" + ("0" * 64),
        "sha256=" + ("A" * 64),
        "sha256=" + ("0" * 65),
        "sha256=" + ("0" * 63),
        "sha256 = " + ("0" * 64),
    ],
)
def test_signature_rejects_noncanonical_encodings(header):
    with pytest.raises(MalformedSignature):
        verify_signature(b"{}", SECRETS, header)


def test_strict_json_rejects_duplicate_nested_keys():
    with pytest.raises(MalformedPayload):
        decode_payload(b'{"outer":{"same":1,"same":2}}')


def test_strict_json_rejects_excessive_nesting():
    body = ("{" + '"x":{' * 65 + '"value":1' + "}" * 66).encode()
    with pytest.raises(MalformedPayload):
        decode_payload(body)


def test_push_created_and_deleted_invariants():
    created = load_fixture("push.json")
    created.update({"before": ZERO_SHA, "created": True})
    created_event = normalize_event("push", created, DELIVERY_A)
    assert created_event.action == "created"
    assert created_event.sha == created["after"]

    deleted = load_fixture("push.json")
    deleted.update({"after": ZERO_SHA, "deleted": True})
    deleted["head_commit"] = None
    deleted["commits"] = []
    deleted_event = normalize_event("push", deleted, DELIVERY_A)
    assert deleted_event.action == "deleted"
    assert deleted_event.sha is None

    impossible = copy.deepcopy(created)
    impossible["deleted"] = True
    with pytest.raises(MalformedPayload):
        normalize_event("push", impossible, DELIVERY_A)


def test_push_rejects_boolean_integer_confusion_and_bad_commit_files():
    payload = load_fixture("push.json")
    payload["forced"] = 1
    with pytest.raises(MalformedPayload):
        normalize_event("push", payload, DELIVERY_A)

    payload = load_fixture("push.json")
    payload["commits"][0]["added"] = ["ok.py", 7]
    with pytest.raises(MalformedPayload):
        normalize_event("push", payload, DELIVERY_A)


def test_pull_request_fork_and_merged_sha_are_normalized():
    payload = load_fixture("pull_request.json")
    payload["pull_request"]["head"]["repo"]["full_name"] = "external/fork"
    fork_event = normalize_event("pull_request", payload, DELIVERY_A)
    assert fork_event.fork is True

    payload["action"] = "closed"
    payload["pull_request"]["merged"] = True
    payload["pull_request"]["merge_commit_sha"] = "a" * 40
    merged_event = normalize_event("pull_request", payload, DELIVERY_A)
    assert merged_event.sha == "a" * 40


@pytest.mark.parametrize(
    ("event_type", "fixture_name", "action"),
    [
        ("pull_request", "pull_request.json", "labeled"),
        ("merge_group", "merge_group.json", "mystery"),
    ],
)
def test_unsupported_event_actions_are_rejected(event_type, fixture_name, action):
    payload = load_fixture(fixture_name)
    payload["action"] = action
    with pytest.raises(UnsupportedEvent):
        normalize_event(event_type, payload, DELIVERY_A)


def test_policy_precedence_and_custom_skip_token():
    payload = load_fixture("push.json")
    payload["commits"][0]["message"] = "automation says NO-BUILD"
    event = normalize_event("push", payload, DELIVERY_A)
    policy = TriggerPolicy(
        allowed_repositories=("vela-org/*",),
        allowed_refs=("refs/heads/*",),
        ignored_refs=("refs/heads/main",),
        blocked_senders=("someone-else",),
        skip_ci_tokens=("no-build",),
    )
    assert evaluate_policy(event, policy).reason == "ignored_ref"

    policy = TriggerPolicy(
        allowed_repositories=("vela-org/*",),
        allowed_refs=("refs/heads/*",),
        skip_ci_tokens=("no-build",),
    )
    assert evaluate_policy(event, policy).reason == "skip_ci"


def test_policy_handles_fork_draft_closed_delete_and_destroyed():
    pull = load_fixture("pull_request.json")
    pull["pull_request"]["head"]["repo"]["full_name"] = "external/fork"
    event = normalize_event("pull_request", pull, DELIVERY_A)
    assert evaluate_policy(event, TriggerPolicy()).reason == "fork_pull_request"
    assert evaluate_policy(
        event,
        TriggerPolicy(allow_fork_pull_requests=True),
    ).accepted

    pull["pull_request"]["draft"] = True
    draft = normalize_event("pull_request", pull, DELIVERY_A)
    assert evaluate_policy(
        draft,
        TriggerPolicy(allow_fork_pull_requests=True),
    ).reason == "draft_pull_request"

    deleted = load_fixture("push.json")
    deleted.update({"after": ZERO_SHA, "deleted": True, "head_commit": None, "commits": []})
    assert evaluate_policy(
        normalize_event("push", deleted, DELIVERY_A),
        TriggerPolicy(),
    ).reason == "deleted_ref"

    group = load_fixture("merge_group.json")
    group["action"] = "destroyed"
    assert evaluate_policy(
        normalize_event("merge_group", group, DELIVERY_A),
        TriggerPolicy(),
    ).reason == "merge_group_destroyed"


def test_replay_stale_reservation_cannot_commit_over_new_generation():
    now = [10.0]
    cache = ReplayCache(5, 1, clock=lambda: now[0])
    stale = cache.reserve(DELIVERY_A, "same")
    now[0] = 16.0
    current = cache.reserve(DELIVERY_A, "same")
    with pytest.raises(ValueError):
        cache.commit(stale, "stale")
    cache.commit(current, "current")
    assert cache.reserve(DELIVERY_A, "same").result == "current"


def test_replay_expired_reservation_cannot_be_committed_directly():
    now = [10.0]
    cache = ReplayCache(5, 1, clock=lambda: now[0])
    expired = cache.reserve(DELIVERY_A, "same")
    now[0] = 16.0
    with pytest.raises(ValueError):
        cache.commit(expired, "too late")
    assert len(cache) == 0


def test_replay_capacity_evicts_oldest_committed_entry():
    cache = ReplayCache(60, 2, clock=lambda: 10.0)
    first = cache.reserve(DELIVERY_A, "a")
    cache.commit(first, "first")
    second = cache.reserve(DELIVERY_B, "b")
    cache.commit(second, "second")

    cache.reserve(DELIVERY_C, "c")
    assert cache.reserve(DELIVERY_B, "b").duplicate is True
    replacement = cache.reserve(DELIVERY_A, "a")
    assert replacement.duplicate is False


def test_replay_capacity_never_evicts_in_progress_entries():
    cache = ReplayCache(60, 1)
    cache.reserve(DELIVERY_A, "a")
    with pytest.raises(ReplayCapacityExceeded):
        cache.reserve(DELIVERY_B, "b")


def test_replay_reservation_is_atomic_across_threads():
    cache = ReplayCache(60, 10)
    barrier = threading.Barrier(3)
    outcomes = []

    def reserve():
        barrier.wait()
        try:
            outcomes.append(cache.reserve(DELIVERY_A, "fingerprint"))
        except Exception as exc:
            outcomes.append(exc)

    threads = [threading.Thread(target=reserve) for _ in range(2)]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join()

    assert sum(not isinstance(value, Exception) for value in outcomes) == 1
    assert sum(isinstance(value, DeliveryInProgress) for value in outcomes) == 1


def test_processor_accepts_case_insensitive_headers_and_quoted_utf8():
    body = encode(load_fixture("push.json"))
    headers = {
        "CONTENT-TYPE": 'Application/JSON; Charset="UTF-8"',
        "X-GITHUB-EVENT": "push",
        "X-GITHUB-DELIVERY": DELIVERY_A,
        "X-HUB-SIGNATURE-256": sign(body),
    }
    result = WebhookProcessor(SECRETS).process(headers, body)
    assert result.event.event == "push"


@pytest.mark.parametrize(
    "secrets",
    [
        {"": "secret"},
        {"id": ""},
        {"id": object()},
    ],
)
def test_processor_validates_secret_entries_at_construction(secrets):
    with pytest.raises((TypeError, ValueError)):
        WebhookProcessor(secrets)


def test_processor_rejects_case_colliding_headers():
    body = encode(load_fixture("push.json"))
    headers = request_headers("push", body)
    headers["Content-Type"] = "application/json"
    with pytest.raises(MalformedHeaders):
        WebhookProcessor(SECRETS).process(headers, body)


@pytest.mark.parametrize(
    "content_type",
    [
        "text/plain",
        "application/json; charset=latin-1",
        "application/json; boundary=something",
        "application/json; charset",
    ],
)
def test_processor_rejects_unsupported_content_types(content_type):
    body = encode(load_fixture("push.json"))
    headers = request_headers("push", body, **{"content-type": content_type})
    with pytest.raises(UnsupportedMediaType):
        WebhookProcessor(SECRETS).process(headers, body)


def test_processor_enforces_size_and_canonical_delivery_uuid():
    processor = WebhookProcessor(
        SECRETS,
        TriggerPolicy(max_payload_bytes=10),
    )
    with pytest.raises(PayloadTooLarge):
        processor.process({}, b"x" * 11)

    body = encode(load_fixture("push.json"))
    uppercase = DELIVERY_A.upper()
    headers = request_headers("push", body, delivery_id=uppercase)
    with pytest.raises(MalformedHeaders):
        WebhookProcessor(SECRETS).process(headers, body)


def test_processor_authenticates_before_decoding_json():
    body = b"{not-json"
    headers = request_headers("push", body)
    headers["x-hub-signature-256"] = "sha256=" + ("0" * 64)
    with pytest.raises(InvalidSignature):
        WebhookProcessor(SECRETS).process(headers, body)


def test_processor_aborts_failed_normalization_for_retry():
    processor = WebhookProcessor(SECRETS)
    invalid_payload = load_fixture("push.json")
    del invalid_payload["repository"]
    invalid_body = encode(invalid_payload)

    with pytest.raises(MalformedPayload):
        processor.process(request_headers("push", invalid_body), invalid_body)

    valid_body = encode(load_fixture("push.json"))
    result = processor.process(request_headers("push", valid_body), valid_body)
    assert result.decision.accepted


def test_processor_rejects_conflicting_completed_delivery():
    processor = WebhookProcessor(SECRETS)
    first_body = encode(load_fixture("push.json"))
    processor.process(request_headers("push", first_body), first_body)

    second_payload = load_fixture("push.json")
    second_payload["after"] = "f" * 40
    second_body = encode(second_payload)
    with pytest.raises(ReplayConflict):
        processor.process(request_headers("push", second_body), second_body)


def test_processor_caches_policy_rejections_as_completed_results():
    body = encode(load_fixture("push.json"))
    processor = WebhookProcessor(
        SECRETS,
        TriggerPolicy(allowed_repositories=("another-org/*",)),
    )
    first = processor.process(request_headers("push", body), body)
    second = processor.process(request_headers("push", body), body)
    assert isinstance(first, DeliveryResult)
    assert first.decision.reason == "repository_not_allowed"
    assert second.duplicate is True
    assert second.decision == first.decision
