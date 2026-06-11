# Reviewer notes

This file is private. Solvers should not see it.

## Task assessment

This is a staff-level SWE / CI integration challenge. It is intentionally much larger than the
original two-helper webhook exercise. The reference patch adds more than 570 nonblank lines
across authentication, strict decoding, three event normalizers, policy evaluation, replay
state, request processing, and evidence outputs.

The task requires several interacting invariants:

- raw-body authentication with multiple rotating secrets and no early-exit comparison;
- duplicate-key-aware JSON decoding and schema validation where Python bool/int behavior matters;
- event-specific normalization for push, pull request, and merge queue deliveries;
- exact policy precedence with glob matching and case-normalized sender/token checks;
- a bounded concurrent replay state machine with generations, TTL, deterministic eviction,
  cached results, conflicts, aborts, and stale-reservation safety; and
- end-to-end ordering so invalid requests do not poison replay state and authenticated retries
  behave correctly.

The expected frontier pass rate is below 10%. A plausible implementation must span multiple
modules and pass 58 public/private tests, including concurrency and monkeypatched
constant-comparison checks. This is not solvable by copying a short GitHub HMAC example.

## Public contract

The prompt deliberately specifies:

- accepted signature and media-type grammars;
- exact normalized fields and action rules;
- policy reason strings and precedence;
- replay state transitions, capacity behavior, and concurrency requirements;
- processor validation/authentication/reservation ordering; and
- required output schemas.

Hidden tests should therefore identify implementation defects rather than undocumented
preferences.

## Reference solution

The reference patch:

- adds roughly 400 lines to `webhook/github.py`;
- adds roughly 120 lines each to `webhook/replay.py` and `webhook/processor.py`;
- creates `metrics.json` and `report.md`; and
- leaves public APIs, fixtures, models, and exception definitions unchanged.

`verify_signature` evaluates every configured secret with `hmac.compare_digest` before deciding.
`decode_payload` uses `object_pairs_hook` and `parse_constant`. Normalizers use typed helper
validation rather than permissive dictionary access. `ReplayCache` serializes state changes with
a lock and uses reservation tokens to prevent stale commits. `WebhookProcessor` authenticates
before decoding and aborts only the current reservation generation on downstream failure.

## Hidden test coverage

The private suite independently checks:

- every secret is compared even when the first secret matches;
- malformed canonicalization and invalid secret configurations;
- nested duplicate keys and depth limits;
- push creation/deletion invariants and bool/int confusion;
- pull request fork/merge behavior and unsupported actions;
- policy precedence, custom skip tokens, and event-specific rejection reasons;
- expired generations, stale commits, deterministic eviction, full in-progress capacity, and
  two-thread reservation races;
- case-insensitive and case-colliding headers;
- media-type parameters, payload limits, and canonical UUIDs;
- authentication-before-decoding;
- replay abort followed by a corrected request;
- completed-delivery conflicts; and
- caching of policy-rejected results.

## Common incomplete solutions

- Returning after the first matching secret, leaking rotation order through work performed.
- Using ordinary `json.loads` and silently accepting duplicate keys or `NaN`.
- Treating booleans as valid integer IDs because `bool` subclasses `int`.
- Applying policy before complete event normalization or using the wrong rejection precedence.
- Implementing replay protection as a set without in-progress state, fingerprints, generations,
  cached results, or locking.
- Evicting in-progress work at capacity.
- Reserving before signature verification or failing to abort after normalization errors.
- Recomputing duplicate results instead of returning the committed result.
- Trusting hardcoded metrics while public or private tests fail.
