# Build a production-grade GitHub webhook delivery pipeline

Vela currently exposes the public types for GitHub webhook processing, but the implementation
in `webhook/github.py`, `webhook/replay.py`, and `webhook/processor.py` is stubbed. Implement the
complete delivery pipeline without changing the existing public function, method, dataclass, or
exception definitions.

The pipeline must authenticate the exact raw request body, decode unambiguous JSON, normalize
three GitHub event families, apply trigger policy, and provide bounded thread-safe replay
protection. Tests must be local and deterministic; do not call GitHub or any other network
service.

## 1. Signature verification and secret rotation

Implement `verify_signature` with these requirements:

- `signature_header=None` raises `MissingHeader`.
- Every other malformed value raises `MalformedSignature`.
- The only accepted format is exactly `sha256=` followed by 64 lowercase hexadecimal
  characters. Do not trim whitespace, accept SHA-1, accept uppercase encodings, or accept
  abbreviated digests.
- Secret IDs are non-empty strings. Secret values are non-empty `str` or `bytes` values. An
  empty mapping or invalid configuration raises `TypeError` or `ValueError`.
- Compute HMAC-SHA256 over the exact `payload_body` bytes for every configured secret and use
  `hmac.compare_digest` for every comparison. Do not stop comparing after the first match.
- Return the first matching secret ID in mapping iteration order. If no secret matches, raise
  `InvalidSignature`.

## 2. Strict payload decoding

Implement `decode_payload` so it:

- accepts bytes containing UTF-8 JSON;
- rejects invalid UTF-8, invalid JSON, duplicate object keys at any nesting level, `NaN`,
  `Infinity`, and `-Infinity`;
- requires a JSON object at the top level; and
- rejects payloads nested more than 64 container levels.

All data errors from this function raise `MalformedPayload`.

## 3. Event normalization

Implement `normalize_event` for `push`, `pull_request`, and `merge_group`. Unknown event names
and unsupported actions raise `UnsupportedEvent`. Missing fields, wrong types, invalid refs, or
invalid SHAs raise `MalformedPayload`.

Common rules:

- `repository.full_name` and `sender.login` are required non-empty strings.
- Repository full names must contain exactly one `/`, with non-empty owner and repository
  components and no whitespace.
- `installation` may be absent or null. When present, `installation.id` is a positive integer;
  booleans are not integers.
- Git object IDs are exactly 40 lowercase hexadecimal characters.
- Full refs start with `refs/` and contain no whitespace.

### Push

Require `ref`, `before`, `after`, `created`, `deleted`, and `forced`.

- A created push has an all-zero `before` SHA and action `created`.
- A deleted push has an all-zero `after` SHA, action `deleted`, and normalized `sha=None`.
- A push cannot be both created and deleted.
- Other pushes use action `forced` when forced, otherwise `updated`, and use `after` as `sha`.
- `commits` defaults to an empty array. Each entry requires `id` and `message`.
- `added`, `modified`, and `removed` default to empty arrays on commits and `head_commit`.
  Validate every filename as a non-empty string.
- Normalize commit IDs in input order. Normalize messages as the `head_commit` message first
  when present, followed by every commit message in input order without de-duplicating equal
  strings. Normalize changed files as a sorted de-duplicated tuple, including `head_commit`
  files.
- Set `skip_ci` when a normalized message contains `[skip ci]` or `[ci skip]`,
  case-insensitively.

### Pull request

Support actions `opened`, `reopened`, `synchronize`, `ready_for_review`, and `closed`.

- Require a positive `number`, boolean `draft` and `merged`, head and base branch names and SHAs,
  and `head.repo.full_name`.
- Branch names are not full refs, do not start or end with `/`, and contain no whitespace.
- Normalize `ref` as `refs/pull/<number>/head` and `base_ref` as `refs/heads/<base branch>`.
- Use the head SHA normally. For a closed merged pull request, require a non-null valid
  `merge_commit_sha` and use it as the normalized SHA.
- Set `fork` by comparing the head repository full name to the delivery repository
  case-insensitively.

### Merge group

Support actions `checks_requested` and `destroyed`. Require `head_sha`, `head_ref`, `base_sha`,
and `base_ref` from `merge_group`, and copy them into the normalized model.

## 4. Trigger policy

Implement `evaluate_policy` with case-sensitive shell-style matching for repository and ref
patterns. Sender blocking is case-insensitive. Return `PolicyDecision` using the following
first-match precedence and exact reason strings:

1. event absent from `allowed_events`: `event_not_allowed`
2. repository not matching `allowed_repositories`: `repository_not_allowed`
3. blocked sender: `blocked_sender`
4. ref matching `ignored_refs`: `ignored_ref`
5. ref not matching `allowed_refs`: `ref_not_allowed`
6. any configured skip token found case-insensitively in normalized messages: `skip_ci`
7. deleted push: `deleted_ref`
8. closed pull request: `pull_request_closed`
9. draft pull request: `draft_pull_request`
10. disallowed fork pull request: `fork_pull_request`
11. destroyed merge group: `merge_group_destroyed`

Otherwise return `PolicyDecision(True, "accepted")`.

## 5. Atomic replay cache

Implement `ReplayCache` as a thread-safe, bounded reservation cache:

- `ttl_seconds` must be a positive finite non-boolean number and `capacity` must be a positive
  non-boolean integer. Use the injected callable clock or `time.monotonic`; clock results must
  also be finite non-boolean numbers.
- `reserve(delivery_id, fingerprint)` atomically creates an in-progress reservation.
- Reserving the same ID and fingerprint while in progress raises `DeliveryInProgress`.
- Reserving the same ID with a different fingerprint raises `ReplayConflict`, whether the
  existing entry is in progress or committed.
- Reserving a committed ID with the same fingerprint returns a duplicate `Reservation`
  containing the exact cached result.
- `commit` accepts only the current non-duplicate reservation, stores the result, and refreshes
  its TTL. A stale, aborted, expired, or superseded reservation raises `ValueError`.
- `abort` removes only the matching in-progress generation and is otherwise harmless.
- Expired in-progress and committed entries are removed before cache operations and `len(cache)`.
- At capacity, evict the oldest committed entry by reservation order. Never evict an
  in-progress entry. Raise `ReplayCapacityExceeded` if all entries are in progress.
- Concurrent calls for the same new delivery must produce exactly one reservation.

## 6. End-to-end processor

Implement `WebhookProcessor`:

- Copy and validate the secret mapping at construction. Use the supplied policy or defaults.
- Build a `ReplayCache` from policy TTL/capacity unless one is injected.
- `process` accepts only a byte body and rejects bodies over `max_payload_bytes` before other
  request work.
- Header names are case-insensitive, but two mapping keys that collide case-insensitively are
  ambiguous and raise `MalformedHeaders`. Header names and values must be strings.
- Require non-empty `Content-Type`, `X-GitHub-Event`, `X-GitHub-Delivery`, and
  `X-Hub-Signature-256`.
- Accept `application/json` case-insensitively with no parameter or exactly one
  `charset=utf-8` (quoted or unquoted, case-insensitive). Reject all other media types and
  parameter counts or values with `UnsupportedMediaType`.
- Require `X-GitHub-Delivery` to be the canonical lowercase string form of a UUID.
- Verify the signature over the exact body before JSON decoding.
- Fingerprint the event name plus the raw body and reserve immediately after authentication,
  before JSON decoding. This ensures any authenticated change to the event or body conflicts
  under an existing delivery ID.
- Abort the reservation on decoding, normalization, policy, or result construction failure so
  a corrected delivery can retry.
- Cache both accepted and policy-rejected results.
- For an exact committed duplicate, return the cached `DeliveryResult` with only
  `duplicate=True` changed.

## Tests and required outputs

Expand or maintain `tests/test_github_webhook.py`. The public suite must contain at least 20
passing tests and cover the major behaviors above.

Run:

```bash
bash .shipd/public/setup.sh
. .venv/bin/activate
python -m pytest tests/test_github_webhook.py -q
```

Create `metrics.json` with:

- integer `tests_passed`
- integer `tests_total`
- `signature_rotation_verified`
- `strict_json_verified`
- `event_normalization_verified`
- `replay_protection_verified`
- `policy_verified`

The counts must match and be at least 20. Every verification field must be the JSON boolean
`true`.

Create `report.md` with the reproducible setup/test command and concise notes covering rotating
HMAC secrets, duplicate-key rejection, replay behavior, and all three supported event names.
