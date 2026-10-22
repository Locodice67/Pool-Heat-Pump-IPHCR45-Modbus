import asyncio
import logging

from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)
_PROBE_INTERVAL = 5  # une tentative de reconnexion toutes les N cycles de poll ignorés


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
        """Enregistre un callback appelé après chaque cycle de poll réussi
        (piloté par le même timer que les capteurs, cf. update_sensors)."""
        self._poll_listeners.append(callback)

    def remove_poll_listener(self, callback):
        self._poll_listeners = [cb for cb in self._poll_listeners if cb is not callback]

    def start(self) -> None:
        """Démarre le timer de poll. Sans I/O : ne doit jamais bloquer le setup."""
        self._start_polling()

    async def async_initial_poll(self) -> None:
        """Connexion + premier cycle, hors setup (exécuté en tâche de fond)."""
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
        """Indirection nécessaire : au moment où start() enregistre le timer
        (avant que les plateformes soient chargées), self._update_callback est
        encore le no-op passé par __init__.py. sensor.py le remplace ensuite par
        update_sensors ; passer l'attribut directement à async_track_time_interval
        figerait la référence d'origine. On relit donc l'attribut à chaque
        déclenchement."""
        # Sonde de reconnexion : liaison jugée HS et aucune tentative encore
        # comptée par should_skip_poll() -> on recycle la connexion avant le
        # cycle. Jamais pendant l'hivernage (aucune I/O Modbus).
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
        """Active l'hivernage : plus aucune I/O Modbus tant qu'il est actif."""
        self.hivernage = enabled
        self._modbus_fail_count = 0
        self._probe_counter = 0
        if enabled:
            self.modbus_ok = False

    def add_state_listener(self, callback) -> None:
        """Enregistre un rappel qui réécrit l'état d'une entité (sans I/O)."""
        if callback not in self._state_listeners:
            self._state_listeners.append(callback)

    def refresh_states(self) -> None:
        """Réécrit l'état de toutes les entités, sans aucune I/O Modbus.

        Utilisé à la bascule de l'hivernage : la disponibilité des entités doit
        suivre immédiatement, sans les recréer et sans lancer de lecture.
        On ne passe jamais par `homeassistant.update_entity`, qui appellerait
        `async_update()` et déclencherait donc du trafic Modbus.
        """
        for callback in list(self._state_listeners):
            entity = getattr(callback, "__self__", None)
            if entity is not None and getattr(entity, "hass", None) is None:
                # Entité retirée entre-temps : on purge le rappel mort.
                self._state_listeners.remove(callback)
                continue
            callback()

    def should_skip_poll(self) -> bool:
        """True si le poll doit être sauté car la PAC est déconnectée.

        Autorise quand même une tentative de reconnexion toutes les
        _PROBE_INTERVAL cycles, sinon la connexion ne se rétablirait jamais.
        """
        if self.hivernage:
            return True
        if self._modbus_fail_count < self._modbus_fail_threshold:
            return False
        self._probe_counter += 1
        if self._probe_counter >= _PROBE_INTERVAL:
            self._probe_counter = 0
            _LOGGER.debug("Modbus déconnecté — tentative de reconnexion")
            return False
        _LOGGER.debug(
            "Modbus déconnecté — poll ignoré (%d/%d avant nouvelle tentative)",
            self._probe_counter,
            _PROBE_INTERVAL,
        )
        return True
