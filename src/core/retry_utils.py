import time
import random
import threading
from typing import Callable, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout


class CircuitBreaker:
    """Simple in-memory circuit breaker."""
    def __init__(self, fail_threshold: int = 5, reset_timeout: int = 60):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self._fail_count = 0
        self._last_failure = 0
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            if self._fail_count >= self.fail_threshold:
                # If cooldown not elapsed, deny
                if time.time() - self._last_failure < self.reset_timeout:
                    return False
                # reset
                self._fail_count = 0
            return True

    def record_failure(self):
        with self._lock:
            self._fail_count += 1
            self._last_failure = time.time()

    def record_success(self):
        with self._lock:
            self._fail_count = 0
            self._last_failure = 0


def retry_callable(fn: Callable[[], Any], retries: int = 3, backoff_factor: float = 1.0,
                   exceptions: Tuple[type, ...] = (Exception,), jitter: float = 0.1,
                   circuit: CircuitBreaker = None, call_timeout: float = None):
    """Retry a no-arg callable with exponential backoff and optional circuit breaker.

    fn: callable that takes no args and returns a value or raises.
    """
    if circuit and not circuit.allow():
        raise RuntimeError("Circuit open; skipping call")

    attempt = 0
    while True:
        try:
            if call_timeout:
                with ThreadPoolExecutor(max_workers=1) as ex:
                    future = ex.submit(fn)
                    try:
                        result = future.result(timeout=call_timeout)
                    except FuturesTimeout:
                        raise TimeoutError(f"Call exceeded timeout of {call_timeout}s")
            else:
                result = fn()
            if circuit:
                circuit.record_success()
            return result
        except exceptions as e:
            attempt += 1
            if circuit:
                circuit.record_failure()
            if attempt > retries:
                raise
            sleep_time = backoff_factor * (2 ** (attempt - 1))
            # add jitter
            sleep_time = sleep_time + random.uniform(0, jitter)
            time.sleep(sleep_time)
