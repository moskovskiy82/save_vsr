"""DataUpdateCoordinator for Systemair SAVE VSR."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_UPDATE_INTERVAL
from .hub import VSRHub
from .modbus import IntegerType, ModbusParameter, parameter_map

_LOGGER = logging.getLogger(__name__)

# How many fast polls before doing slow-cycle alarms
SLOW_CYCLE_EVERY = 6

# Maximum gap for block merging in registers (small gaps tolerated)
MAX_BLOCK_GAP = 2

# How long to wait before retrying failed addresses (in polls)
RESET_FAILED_EVERY = 180  # ~30min at 10s interval


class VSRCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Systemair SAVE VSR Modbus integration."""

    def __init__(self, hass: HomeAssistant, hub: VSRHub, update_interval_s: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Systemair VSR Coordinator",
            update_interval=timedelta(seconds=update_interval_s or DEFAULT_UPDATE_INTERVAL),
        )
        self.hub = hub
        self._slow_counter = 0  # Run slow cycle every N fast polls
        self._poll_count = 0  # For resetting failed addresses
        self._failed_addrs: set[int] = set()
        self._failure_count: int = 0

    def get_modbus_data(self, parameter: ModbusParameter) -> float | int | bool:
        """
        Get decoded data for a ModbusParameter from coordinator data.
        
        Automatically handles:
        - Signed/unsigned conversion
        - Scale factors (e.g., temperature × 10)
        - Boolean conversion
        - 32-bit register combinations
        """
        if self.data is None:
            return 0

        # Get raw value from data dict (keyed by parameter short name)
        raw_value = self.data.get(parameter.short)
        if raw_value is None:
            return 0

        # Handle boolean parameters
        if parameter.boolean:
            return bool(raw_value)

        # Handle 32-bit combined registers
        if parameter.combine_with_32_bit:
            high_param = next(
                (p for p in parameter_map.values() if p.register == parameter.combine_with_32_bit),
                None,
            )
            if high_param:
                high_value = self.data.get(high_param.short, 0)
                raw_value = raw_value + (high_value << 16)

        # Convert signed integers
        if parameter.sig == IntegerType.INT and raw_value > 32767:
            raw_value = raw_value - 65536

        # Apply scale factor
        if parameter.scale_factor:
            return raw_value / parameter.scale_factor

        return raw_value

    async def _batch_read_type(
        self, entries: list[tuple[int, int, int]], is_input: bool
    ) -> dict[int, list[int] | None]:
        """
        Do grouped reads for either input or holding registers.
        
        Args:
            entries: List of (index, address, count) tuples
            is_input: True for input registers, False for holding
            
        Returns:
            Mapping of index -> list[int] | None
        """
        if not entries:
            return {}

        entries_sorted = sorted(entries, key=lambda x: x[1])
        blocks: list[dict] = []
        cur_block = None

        # Merge nearby registers into blocks
        for idx, addr, cnt in entries_sorted:
            if addr in self._failed_addrs:
                continue

            new_end = addr + cnt - 1
            if cur_block is None:
                cur_block = {"start": addr, "end": new_end, "items": [(idx, addr, cnt)]}
                continue

            if addr <= cur_block["end"] + MAX_BLOCK_GAP + 1:
                cur_block["end"] = max(cur_block["end"], new_end)
                cur_block["items"].append((idx, addr, cnt))
            else:
                blocks.append(cur_block)
                cur_block = {"start": addr, "end": new_end, "items": [(idx, addr, cnt)]}

        if cur_block:
            blocks.append(cur_block)

        # Read all blocks
        results: dict[int, list[int] | None] = {}
        for block in blocks:
            start = block["start"]
            nregs = block["end"] - block["start"] + 1
            try:
                regs = (
                    await self.hub.read_input(start, nregs)
                    if is_input
                    else await self.hub.read_holding(start, nregs)
                )
            except Exception as exc:
                _LOGGER.warning("Batch read failed at %s (count=%s): %s", start, nregs, exc)
                regs = None

            if regs is None:
                self._failure_count += 1
                for idx, addr, cnt in block["items"]:
                    self._failed_addrs.add(addr)
                    results[idx] = None
            else:
                for idx, addr, cnt in block["items"]:
                    offset = addr - start
                    part = regs[offset : offset + cnt] if offset + cnt <= len(regs) else regs[offset:]
                    results[idx] = part if part else None

        return results

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            # Preserve previous data to avoid losing slow-cycle values
            data: dict[str, Any] = self.data.copy() if self.data else {}

            # Reset failed addresses periodically
            self._poll_count += 1
            if self._poll_count % RESET_FAILED_EVERY == 0:
                self._failed_addrs.clear()
                _LOGGER.debug("Reset failed addresses for periodic retry")

            # Build list of parameters to read (fast cycle)
            fast_params = [
                parameter_map["REG_MODE_MAIN_STATUS_IN"],
                parameter_map["REG_MODE_SPEED"],
                parameter_map["REG_TARGET_TEMP"],
                parameter_map["REG_TEMP_OUTDOOR"],
                parameter_map["REG_TEMP_SUPPLY"],
                parameter_map["REG_TEMP_EXHAUST"],
                parameter_map["REG_TEMP_EXTRACT"],
                parameter_map["REG_TEMP_OVERHEAT"],
                parameter_map["REG_SAF_RPM"],
                parameter_map["REG_EAF_RPM"],
                parameter_map["REG_SUPPLY_FAN_PCT"],
                parameter_map["REG_EXTRACT_FAN_PCT"],
                parameter_map["REG_HEATER_PERCENT"],
                parameter_map["REG_HEAT_EXCH_STATE"],
                parameter_map["REG_ROTOR"],
                parameter_map["REG_HEATER"],
                parameter_map["REG_SETPOINT_ECO_OFFSET"],
                parameter_map["REG_MODE_SUMMERWINTER"],
                parameter_map["REG_FAN_RUNNING_START"],
                parameter_map["REG_DAMPER_STATE"],
                parameter_map["REG_COOLING_RECOVERY"],
                parameter_map["REG_USERMODE_REMAIN"],
                parameter_map["REG_USERMODE_FACTOR"],
                parameter_map["REG_HOLIDAY_DAYS"],
                parameter_map["REG_AWAY_HOURS"],
                parameter_map["REG_FIREPLACE_MINS"],
                parameter_map["REG_REFRESH_MINS"],
                parameter_map["REG_CROWDED_HOURS"],
            ]

            # PART 1 COMPLETE - Continue in Part 2
            return await self._read_and_decode_data(data, fast_params)

        except Exception as err:
            raise UpdateFailed(f"Coordinator update error: {err}") from err

    async def _read_and_decode_data(
        self, data: dict[str, Any], fast_params: list[ModbusParameter]
    ) -> dict[str, Any]:
        """Read registers and decode data (Part 2 of update)."""
        # Add slow cycle parameters (alarms + switches)
        self._slow_counter += 1
        run_slow = self._slow_counter >= SLOW_CYCLE_EVERY
        if self.data is None:
            run_slow = True  # Force slow on first poll

        if run_slow:
            self._slow_counter = 0
            slow_params = [
                parameter_map["REG_ALARM_SAF"],
                parameter_map["REG_ALARM_EAF"],
                parameter_map["REG_ALARM_FROST_PROT"],
                parameter_map["REG_ALARM_SAF_RPM"],
                parameter_map["REG_ALARM_EAF_RPM"],
                parameter_map["REG_ALARM_FPT"],
                parameter_map["REG_ALARM_OAT"],
                parameter_map["REG_ALARM_SAT"],
                parameter_map["REG_ALARM_RAT"],
                parameter_map["REG_ALARM_EAT"],
                parameter_map["REG_ALARM_ECT"],
                parameter_map["REG_ALARM_EFT"],
                parameter_map["REG_ALARM_OHT"],
                parameter_map["REG_ALARM_EMT"],
                parameter_map["REG_ALARM_BYS"],
                parameter_map["REG_ALARM_SEC_AIR"],
                parameter_map["REG_ALARM_FILTER"],
                parameter_map["REG_ALARM_RH"],
                parameter_map["REG_ALARM_LOW_SAT"],
                parameter_map["REG_ALARM_PDM_RHS"],
                parameter_map["REG_ALARM_PDM_EAT"],
                parameter_map["REG_ALARM_MAN_FAN_STOP"],
                parameter_map["REG_ALARM_OVERHEAT_TEMP"],
                parameter_map["REG_ALARM_FIRE"],
                parameter_map["REG_ALARM_FILTER_WARN"],
                parameter_map["REG_ALARM_TYPE_A"],
                parameter_map["REG_ALARM_TYPE_B"],
                parameter_map["REG_ALARM_TYPE_C"],
                parameter_map["REG_ECO_MODE_ENABLE"],
                parameter_map["REG_HEATER_ENABLE"],
                parameter_map["REG_RH_TRANSFER_ENABLE"],
            ]
            fast_params.extend(slow_params)

        # Build descriptors for batch reading
        descriptors: list[tuple[bool, int, int]] = []
        param_map_by_index: dict[int, ModbusParameter] = {}

        for i, param in enumerate(fast_params):
            is_input = param.reg_type.value == "Input"
            count = 2 if param.short == "REG_FAN_RUNNING_START" else 1
            descriptors.append((is_input, param.register, count))
            param_map_by_index[i] = param

        # Split into input vs holding
        input_entries: list[tuple[int, int, int]] = []
        holding_entries: list[tuple[int, int, int]] = []
        for i, (is_input, addr, cnt) in enumerate(descriptors):
            (input_entries if is_input else holding_entries).append((i, addr, cnt))

        # Batch read
        input_results = await self._batch_read_type(input_entries, is_input=True)
        holding_results = await self._batch_read_type(holding_entries, is_input=False)

        # Combine results
        results: list[list[int] | None] = []
        for i, (is_input, _addr, _cnt) in enumerate(descriptors):
            results.append(input_results.get(i) if is_input else holding_results.get(i))

        # Store raw values using parameter short names
        for i, result in enumerate(results):
            if result is None:
                continue
            param = param_map_by_index[i]
            if param.short == "REG_FAN_RUNNING_START" and len(result) >= 2:
                data["fan_running"] = result[0]
                data["cooldown"] = result[1]
            else:
                data[param.short] = result[0]

        # Decode values using get_modbus_data
        mode_main_raw = data.get("REG_MODE_MAIN_STATUS_IN")
        if mode_main_raw is not None:
            data["mode_main"] = mode_main_raw
            _LOGGER.debug("Read REG_MODE_MAIN_STATUS_IN (1160): value=%s", mode_main_raw)

        data["mode_speed"] = data.get("REG_MODE_SPEED")
        data["target_temp"] = self.get_modbus_data(parameter_map["REG_TARGET_TEMP"])
        data["temp_outdoor"] = self.get_modbus_data(parameter_map["REG_TEMP_OUTDOOR"])
        data["temp_supply"] = self.get_modbus_data(parameter_map["REG_TEMP_SUPPLY"])
        data["temp_exhaust"] = self.get_modbus_data(parameter_map["REG_TEMP_EXHAUST"])
        data["temp_extract"] = self.get_modbus_data(parameter_map["REG_TEMP_EXTRACT"])
        data["temp_overheat"] = self.get_modbus_data(parameter_map["REG_TEMP_OVERHEAT"])
        data["saf_rpm"] = data.get("REG_SAF_RPM")
        data["eaf_rpm"] = data.get("REG_EAF_RPM")
        data["fan_supply"] = data.get("REG_SUPPLY_FAN_PCT")
        data["fan_extract"] = data.get("REG_EXTRACT_FAN_PCT")
        data["heater_percentage"] = data.get("REG_HEATER_PERCENT")
        data["heat_exchanger_state"] = data.get("REG_HEAT_EXCH_STATE")
        data["rotor"] = data.get("REG_ROTOR")
        data["heater"] = data.get("REG_HEATER")
        data["setpoint_eco_offset"] = self.get_modbus_data(parameter_map["REG_SETPOINT_ECO_OFFSET"])
        data["mode_summerwinter"] = self.get_modbus_data(parameter_map["REG_MODE_SUMMERWINTER"])
        data["fan_running"] = bool(data.get("fan_running", 0))
        data["cooldown"] = bool(data.get("cooldown", 0))
        data["damper_state"] = self.get_modbus_data(parameter_map["REG_DAMPER_STATE"])
        data["cooling_recovery"] = self.get_modbus_data(parameter_map["REG_COOLING_RECOVERY"])
        countdown_s = self.get_modbus_data(parameter_map["REG_USERMODE_REMAIN"])
        data["countdown_time_s"] = int(countdown_s)
        data["countdown_time_s_factor"] = data.get("REG_USERMODE_FACTOR", 0)
        data["holiday_days"] = data.get("REG_HOLIDAY_DAYS")
        data["away_hours"] = data.get("REG_AWAY_HOURS")
        data["fireplace_mins"] = data.get("REG_FIREPLACE_MINS")
        data["refresh_mins"] = data.get("REG_REFRESH_MINS")
        data["crowded_hours"] = data.get("REG_CROWDED_HOURS")

        # Decode alarms and switches (slow cycle only)
        if run_slow:
            data["alarm_saf"] = data.get("REG_ALARM_SAF", 0)
            data["alarm_eaf"] = data.get("REG_ALARM_EAF", 0)
            data["alarm_frost_protect"] = data.get("REG_ALARM_FROST_PROT", 0)
            data["alarm_saf_rpm"] = data.get("REG_ALARM_SAF_RPM", 0)
            data["alarm_eaf_rpm"] = data.get("REG_ALARM_EAF_RPM", 0)
            data["alarm_fpt"] = data.get("REG_ALARM_FPT", 0)
            data["alarm_oat"] = data.get("REG_ALARM_OAT", 0)
            data["alarm_sat"] = data.get("REG_ALARM_SAT", 0)
            data["alarm_rat"] = data.get("REG_ALARM_RAT", 0)
            data["alarm_eat"] = data.get("REG_ALARM_EAT", 0)
            data["alarm_ect"] = data.get("REG_ALARM_ECT", 0)
            data["alarm_eft"] = data.get("REG_ALARM_EFT", 0)
            data["alarm_oht"] = data.get("REG_ALARM_OHT", 0)
            data["alarm_emt"] = data.get("REG_ALARM_EMT", 0)
            data["alarm_bys"] = data.get("REG_ALARM_BYS", 0)
            data["alarm_sec_air"] = data.get("REG_ALARM_SEC_AIR", 0)
            data["alarm_filter"] = data.get("REG_ALARM_FILTER", 0)
            data["alarm_rh"] = data.get("REG_ALARM_RH", 0)
            data["alarm_low_SAT"] = data.get("REG_ALARM_LOW_SAT", 0)
            data["alarm_pdm_rhs"] = data.get("REG_ALARM_PDM_RHS", 0)
            data["alarm_pdm_eat"] = data.get("REG_ALARM_PDM_EAT", 0)
            data["alarm_man_fan_stop"] = data.get("REG_ALARM_MAN_FAN_STOP", 0)
            data["alarm_overheat_temp"] = data.get("REG_ALARM_OVERHEAT_TEMP", 0)
            data["alarm_fire"] = data.get("REG_ALARM_FIRE", 0)
            data["alarm_filter_warn"] = data.get("REG_ALARM_FILTER_WARN", 0)
            data["alarm_typeA"] = data.get("REG_ALARM_TYPE_A", 0)
            data["alarm_typeB"] = data.get("REG_ALARM_TYPE_B", 0)
            data["alarm_typeC"] = data.get("REG_ALARM_TYPE_C", 0)
            data["eco_mode"] = self.get_modbus_data(parameter_map["REG_ECO_MODE_ENABLE"])
            data["heater_enable"] = self.get_modbus_data(parameter_map["REG_HEATER_ENABLE"])
            data["rh_transfer"] = self.get_modbus_data(parameter_map["REG_RH_TRANSFER_ENABLE"])

        # Add diagnostics
        data["modbus_failures"] = self._failure_count

        return data
