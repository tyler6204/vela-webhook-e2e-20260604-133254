"""Bounded, thread-safe replay protection for GitHub delivery IDs."""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class Reservation:
    delivery_id: str
    fingerprint: str
    token: Optional[int]
    duplicate: bool
    result: object = None


class ReplayCache:
    """Reserve, commit, and abort delivery IDs atomically."""

    def __init__(
        self,
        ttl_seconds: float,
        capacity: int,
        clock: Optional[Callable[[], float]] = None,
    ) -> None:
        raise NotImplementedError

    def reserve(self, delivery_id: str, fingerprint: str) -> Reservation:
        raise NotImplementedError

    def commit(self, reservation: Reservation, result: object) -> None:
        raise NotImplementedError

    def abort(self, reservation: Reservation) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError
