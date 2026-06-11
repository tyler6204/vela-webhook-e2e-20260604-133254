"""End-to-end GitHub webhook delivery processor."""

from typing import Mapping, Optional

from .models import DeliveryResult, TriggerPolicy
from .replay import ReplayCache


class WebhookProcessor:
    def __init__(
        self,
        secrets: Mapping[str, object],
        policy: Optional[TriggerPolicy] = None,
        replay_cache: Optional[ReplayCache] = None,
    ) -> None:
        raise NotImplementedError

    def process(self, headers: Mapping[str, str], body: bytes) -> DeliveryResult:
        raise NotImplementedError
