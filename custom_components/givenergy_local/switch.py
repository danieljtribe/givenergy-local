"""Switch sensor platform."""
from __future__ import annotations

from typing import Any

from givenergy_modbus.client import GivEnergyClient
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Icon
from .coordinator import GivEnergyUpdateCoordinator
from .entity import InverterEntity
from .givenergy_ext import async_reliable_call


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add switches for passed config_entry in HA."""
    coordinator: GivEnergyUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            InverterACChargingSwitch(
                coordinator, config_entry
            ),
            InverterBatteryDischargingSwitch(
                coordinator, config_entry
            ),
        ]
    )


class InverterACChargingSwitch(InverterEntity, SwitchEntity):
    """Controls AC charging."""

    entity_description = SwitchEntityDescription(
        key="enable_charge",
        icon=Icon.BATTERY_PLUS,
        name="Battery AC Charging",
    )

    def __init__(
        self,
        coordinator: GivEnergyUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = (
            f"{self.data.inverter_serial_number}_{self.entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self.data.enable_charge  # type: ignore

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable AC charging, subject to charge slot configuration."""

        def enable_ac_charge(client: GivEnergyClient) -> None:
            client.enable_charge()

        await async_reliable_call(
            self.hass,
            self.coordinator,
            enable_ac_charge,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable AC charging, subject to charge slot configuration."""

        def disable_ac_charge(client: GivEnergyClient) -> None:
            client.disable_charge()

        await async_reliable_call(
            self.hass,
            self.coordinator,
            disable_ac_charge,
        )

class InverterBatteryDischargingSwitch(InverterEntity, SwitchEntity):
    """Controls Battery discharging."""

    entity_description = SwitchEntityDescription(
        key="enable_discharge",
        icon=Icon.BATTERY_MINUS,
        name="Battery Discharging",
    )

    def __init__(
        self,
        coordinator: GivEnergyUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = (
            f"{self.data.inverter_serial_number}_{self.entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        return self.data.enable_discharge  # type: ignore

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable Discharging."""

        def enable_discharge(client: GivEnergyClient) -> None:
            client.enable_discharge()

        await async_reliable_call(
            self.hass,
            self.coordinator,
            enable_discharge,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable discharging."""

        def disable_discharge(client: GivEnergyClient) -> None:
            client.disable_discharge()

        await async_reliable_call(
            self.hass,
            self.coordinator,
            disable_discharge,
        )
