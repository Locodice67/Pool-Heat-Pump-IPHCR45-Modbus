from .const import DOMAIN
from .controller import PacController
from .models import DEVICE_NAME


class PacDeviceMixin:
    """device_info shared by all heat pump entities (single device).

    The manufacturer and model come from the model selected at
    configuration time (see models.BRANDS).
    """

    _entry_id: str
    _controller: PacController

    @property
    def available(self) -> bool:
        """Unavailable during wintering (no Modbus I/O)."""
        return not self._controller.hivernage

    @property
    def device_info(self):
        model = self.hass.data[DOMAIN][self._entry_id].get("model_config", {})
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": DEVICE_NAME,
            "manufacturer": model.get("manufacturer"),
            "model": model.get("model"),
        }
