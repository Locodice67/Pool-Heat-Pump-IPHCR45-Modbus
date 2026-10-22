import asyncio
import logging

from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)
_PROBE_INTERVAL = 5  # one reconnection attempt every N skipped poll cycles


class PacController:
    def __init__(
        self, hass, update_callback, scan_interval, handler, hivernage=False
    ):
        self._hass = hass
        self._update_callback = update_callback
        self._scan_interval = scan_interval
        self._remove_listener = None
        self._handler = handler
        self.modbus_ok = False
        self.hivernage = bool(hivernage)
        self._state_listeners = []
        self._modbus_fail_count = 0
        self._modbus_fail_threshold = 3
        self._probe_counter = 0
        self._poll_listeners = []

    @property
    def scan_interval(self):
        return self._scan_interval

    @property
    def handler(self):
        return self._handler

    def add_poll_listener(self, callback):
        """Register a callback called after each successful poll cycle
        (driven by the same timer as the sensors, cf. update_sensors)."""
        self._poll_listeners.append(callback)

    def remove_poll_listener(self, callback):
        self._poll_listeners = [cb for cb in self._poll_listeners if cb is not callback]

    def start(self) -> None:
        """Start the poll timer. No I/O: must never block setup."""
        self._start_polling()

    async def async_initial_poll(self) -> None:
        """Connect + first cycle, outside setup (run as a background task)."""
        if self.hivernage:
            return
        self.modbus_ok = await self._handler.connect()
        await self._dispatch_update(None)

    async def stop(self):
        if self._remove_listener:
            self._remove_listener()
            self._remove_listener = None
        await self._handler.close()

    def _start_polling(self):
        if self._remove_listener:
            self._remove_listener()
        self._remove_listener = async_track_time_interval(
            self._hass, self._dispatch_update, timedelta(seconds=self._scan_interval)
        )

    async def _dispatch_update(self, now):
        """Required indirection: when start() registers the timer
        (before the platforms are loaded), self._update_callback is still
        the no-op passed by __init__.py. sensor.py then replaces it with
        update_sensors; passing the attribute directly to
        async_track_time_interval would freeze the original reference. So
        the attribute is re-read on every trigger."""
        # Reconnection probe: link considered down and no attempt yet
        # counted by should_skip_poll() -> recycle the connection before the
        # cycle. Never during wintering (no Modbus I/O).
        if not self.hivernage and not self.modbus_ok and self._probe_counter == 0:
            await self._handler.reconnect()
        result = self._update_callback(now)
        if asyncio.iscoroutine(result):
            await result

    async def update_interval(self, new_interval):
        self._scan_interval = new_interval
        self._modbus_fail_count = 0
        self._probe_counter = 0
        self._start_polling()

    def notify_modbus_success(self):
        self._modbus_fail_count = 0
        self._probe_counter = 0
        self.modbus_ok = True

    def notify_modbus_failure(self):
        self._modbus_fail_count += 1
        if self._modbus_fail_count >= self._modbus_fail_threshold:
            self.modbus_ok = False

    def set_hivernage(self, enabled: bool) -> None:
        """Activate wintering: no more Modbus I/O while it is active."""
        self.hivernage = enabled
        self._modbus_fail_count = 0
        self._probe_counter = 0
        if enabled:
            self.modbus_ok = False

    def add_state_listener(self, callback) -> None:
        """Register a callback that rewrites one entity's state (no I/O)."""
        if callback not in self._state_listeners:
            self._state_listeners.append(callback)

    def refresh_states(self) -> None:
        """Rewrite the state of all entities, without any Modbus I/O.

        Used on wintering toggle: entity availability must follow
        immediately, without recreating entities and without starting a read.
        We never go through `homeassistant.update_entity`, which would call
        `async_update()` and therefore trigger Modbus traffic.
        """
        for callback in list(self._state_listeners):
            entity = getattr(callback, "__self__", None)
            if entity is not None and getattr(entity, "hass", None) is None:
                # Entity removed in the meantime: purge the dead callback.
                self._state_listeners.remove(callback)
                continue
            callback()

    def should_skip_poll(self) -> bool:
        """True if the poll must be skipped because the heat pump is disconnected.

        Still allows one reconnection attempt every
        _PROBE_INTERVAL cycles, otherwise the connection would never recover.
        """
        if self.hivernage:
            return True
        if self._modbus_fail_count < self._modbus_fail_threshold:
            return False
        self._probe_counter += 1
        if self._probe_counter >= _PROBE_INTERVAL:
            self._probe_counter = 0
            _LOGGER.debug("Modbus disconnected - reconnection attempt")
            return False
        _LOGGER.debug(
            "Modbus disconnected - poll skipped (%d/%d before next attempt)",
            self._probe_counter,
            _PROBE_INTERVAL,
        )
        return True
