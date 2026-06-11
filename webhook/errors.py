"""Public exception hierarchy for webhook delivery processing."""


class WebhookError(ValueError):
    """Base class for request errors that callers may report without a traceback."""

    code = "webhook_error"


class MissingHeader(WebhookError):
    code = "missing_header"


class MalformedHeaders(WebhookError):
    code = "malformed_headers"


class PayloadTooLarge(WebhookError):
    code = "payload_too_large"


class UnsupportedMediaType(WebhookError):
    code = "unsupported_media_type"


class MalformedSignature(WebhookError):
    code = "malformed_signature"


class InvalidSignature(WebhookError):
    code = "invalid_signature"


class MalformedPayload(WebhookError):
    code = "malformed_payload"


class UnsupportedEvent(WebhookError):
    code = "unsupported_event"


class ReplayConflict(WebhookError):
    code = "replay_conflict"


class DeliveryInProgress(WebhookError):
    code = "delivery_in_progress"


class ReplayCapacityExceeded(WebhookError):
    code = "replay_capacity_exceeded"
