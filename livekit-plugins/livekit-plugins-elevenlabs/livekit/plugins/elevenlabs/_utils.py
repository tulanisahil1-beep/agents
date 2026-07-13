import time
from collections.abc import Callable, Mapping
from typing import Generic, TypeVar

T = TypeVar("T")


def get_trace_id(headers: Mapping[str, str] | None) -> str | None:
    """Return ElevenLabs ``x-trace-id`` from response headers, if present.

    Missing or empty values return ``None`` so callers do not attach a misleading
    empty trace id to errors.
    """
    if not headers:
        return None
    trace_id = headers.get("x-trace-id")
    if not trace_id:
        return None
    return trace_id


class PeriodicCollector(Generic[T]):
    def __init__(self, callback: Callable[[T], None], *, duration: float) -> None:
        """
        Create a new periodic collector that accumulates values and calls the callback
        after the specified duration if there are values to report.

        Args:
            duration: Time in seconds between callback invocations
            callback: Function to call with accumulated value when duration expires
        """
        self._duration = duration
        self._callback = callback
        self._last_flush_time = time.monotonic()
        self._total: T | None = None

    def push(self, value: T) -> None:
        """Add a value to the accumulator"""
        if self._total is None:
            self._total = value
        else:
            self._total += value  # type: ignore
        if time.monotonic() - self._last_flush_time >= self._duration:
            self.flush()

    def flush(self) -> None:
        """Force callback to be called with current total if non-zero"""
        if self._total is not None:
            self._callback(self._total)
            self._total = None
        self._last_flush_time = time.monotonic()
