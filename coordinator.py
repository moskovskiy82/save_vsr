from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_UPDATE_INTERVAL,
    REG_MODE_MAIN_STATUS_IN,
    REG_MODE_SPEED,
    REG_TARGET_TEMP,
    REG_TEMP_OUTDOOR,
    REG_TEMP_SUPPLY,
    REG_TEMP_EXHAUST,
    REG_TEMP_EXTRACT,
    REG_TEMP_OVERHEAT,
    REG_SAF_RPM,
    REG_EAF_RPM,
    REG_SUPPLY_FAN_PCT,
    REG_EXTRACT_FAN_PCT,
    REG_HEATER_PERCENT,
    REG_HEAT_EXCH_STATE,
    REG_ROTOR,
    REG_HEATER,
    REG_SETPOINT_ECO_OFFSET,
    REG_MODE_SUMMERWINTER,
    REG_FAN_RUNNING_START,
    REG_DAMPER_STATE,
    REG_COOLING_RECOVERY,
    REG_USERMODE_REMAIN,
    REG_USERMODE_FACTOR,
    REG_HOLIDAY_DAYS,
    REG_AWAY_HOURS,
    REG_FIREPLACE_MINS,
    REG_REFRESH_MINS,
    REG_CROWDED_HOURS,
    # alarms
    REG_ALARM_SAF,
    REG_ALARM_EAF,
    REG_ALARM_FROST_PROT,
    REG_ALARM_SAF_RPM,
    REG_ALARM_EAF_RPM,
    REG_ALARM_FPT,
    REG_ALARM_OAT,
    REG_ALARM_SAT,
    REG_ALARM_RAT,
    REG_ALARM_EAT,
    REG_ALARM_ECT,
    REG_ALARM_EFT,
    REG_ALARM_OHT,
    REG_ALARM_EMT,
    REG_ALARM_BYS,
    REG_ALARM_SEC_AIR,
    REG_ALARM_FILTER,
    REG_ALARM_RH,
    REG_ALARM_LOW_SAT,
    REG_ALARM_PDM_RHS,
    REG_ALARM_PDM_EAT,
    REG_ALARM_MAN_FAN_STOP,
    REG_ALARM_OVERHEAT_TEMP,
    REG_ALARM_FIRE,
    REG_ALARM_FILTER_WARN,
    REG_ALARM_TYPE_A,
    # switches (optional)
    REG_ECO_MODE_ENABLE,
    REG_HEATER_ENABLE,
    REG_RH_TRANSFER_ENABLE,
)
from .hub import VSRHub

_LOGGER = logging.getLogger(__name__)

# how many fast polls before doing slow-cycle alarms
SLOW_CYCLE_EVERY = 6


class VSRCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Systemair SAVE VSR Modbus integration."""

    def __init__(self, hass: HomeAssistant, hub: VSRHub, update_interval_s: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Systemair VSR Coordinator",
            update_interval=timedelta(seconds=update_interval_s or DEFAULT_UPDATE_INTERVAL),
        )
        self.hub = hub
        self._fast_counter = 0

    async def _batch_read_type(
        self, entries: List[Tuple[int, int, int]], is_input: bool
    ) -> Dict[int, Optional[List[int]]]:
        """
        Read grouped blocks (entries: list of (index, address, count)).
        Returns mapping index -> list[int] | None
        """
        if not entries:
            return {}
        entries_sorted = sorted(entries, key=lambda x: x[1])

        blocks: List[dict] = []
        cur_block = None
        MAX_GAP = 2

        for idx, addr, cnt in entries_sorted:
            if cur_block is None:
                cur_block = {"start": addr, "end": addr + cnt - 1, "items": [(idx, addr, cnt)]}
                continue
            # Merge if registers are reasonably close
            if addr <= cur_block["end"] + MAX_GAP + 1:
                cur_block["end"] = max(cur_block["end"], addr + cnt - 1)
                cur_block["items"].append((idx, addr, cnt))
            else:
                blocks.append(cur_block)
                cur_block = {"start": addr, "end": addr + cnt - 1, "items": [(idx, addr, cnt)]}
        if cur_block:
            blocks.append(cur_block)

        results: Dict[int, Optional[List[int]]] = {}
        for block in blocks:
            start = block["start"]
            nregs = block["end"] - block["start"] + 1
            try:
                regs = (
                    await self.hub.read_input(start, nregs) if is_input else await self.hub.read_holding(start, nregs)
                )
            except Exception as exc:
                _LOGGER.warning("Batch read failed at %s (count=%s): %s", start, nregs, exc)
                regs = None

            for (idx, addr, cnt) in block["items"]:
                if regs is None:
                    results[idx] = None
                else:
                    offset = addr - start
                    part = regs[offset: offset + cnt] if offset + cnt <= len(regs) else regs[offset:]
                    results[idx] = part if part else None

        return results

    async def _async_update_data(self) -> dict[str, Any]:
        """Main coordinator update: read all descriptors and decode to friendly keys."""
        try:
            # Build descriptor list in a deterministic, explicit order.
            # Each entry is (key, is_input, address, count)
            descriptors: List[Tuple[str, bool, int, int]] = [
                ("mode_main", True, REG_MODE_MAIN_STATUS_IN, 1),
                ("mode_speed", False, REG_MODE_SPEED, 1),
                ("target_temp", False, REG_TARGET_TEMP, 1),
                ("temp_outdoor", False, REG_TEMP_OUTDOOR, 1),
                ("temp_supply", False, REG_TEMP_SUPPLY, 1),
                ("temp_exhaust", False, REG_TEMP_EXHAUST, 1),
                ("temp_extract", False, REG_TEMP_EXTRACT, 1),
                ("temp_overheat", False, REG_TEMP_OVERHEAT, 1),
                ("rpms", False, REG_SAF_RPM, 2),  # SAF/EAF (two regs starting at REG_SAF_RPM)
                ("fan_pcts", False, REG_SUPPLY_FAN_PCT, 2),  # supply/extract % (two regs)
                ("heater_percentage", False, REG_HEATER_PERCENT, 1),
                ("heat_exchanger_state", False, REG_HEAT_EXCH_STATE, 1),
                ("rotor", False, REG_ROTOR, 1),
                ("heater", False, REG_HEATER, 1),
                ("setpoint_eco_offset", False, REG_SETPOINT_ECO_OFFSET, 1),
                ("mode_summerwinter", False, REG_MODE_SUMMERWINTER, 1),
                ("fanrun_cool", False, REG_FAN_RUNNING_START, 2),  # fan_running, cooldown
                ("damper_state", False, REG_DAMPER_STATE, 1),
                ("cooling_recovery", False, REG_COOLING_RECOVERY, 1),
                ("countdown_time_s", True, REG_USERMODE_REMAIN, 1),
                ("countdown_time_s_factor", True, REG_USERMODE_FACTOR, 1),
                ("durations", False, REG_HOLIDAY_DAYS, 5),  # holiday/away/fireplace/refresh/crowded
            ]

            # Add optional switch registers into the FAST cycle (cheap)
            if REG_ECO_MODE_ENABLE is not None:
                descriptors.append(("eco_mode", False, REG_ECO_MODE_ENABLE, 1))
            if REG_HEATER_ENABLE is not None:
                descriptors.append(("heater_enable", False, REG_HEATER_ENABLE, 1))
            if REG_RH_TRANSFER_ENABLE is not None:
                descriptors.append(("rh_transfer", False, REG_RH_TRANSFER_ENABLE, 1))

            # Decide slow cycle: read alarms less frequently
            self._fast_counter += 1
            do_slow = self._fast_counter >= SLOW_CYCLE_EVERY
            if do_slow:
                self._fast_counter = 0
                # append alarms in slow cycle
                alarm_regs = [
                    ("alarm_saf", False, REG_ALARM_SAF, 1),
                    ("alarm_eaf", False, REG_ALARM_EAF, 1),
                    ("alarm_frost_protect", False, REG_ALARM_FROST_PROT, 1),
                    ("alarm_saf_rpm", False, REG_ALARM_SAF_RPM, 1),
                    ("alarm_eaf_rpm", False, REG_ALARM_EAF_RPM, 1),
                    ("alarm_fpt", False, REG_ALARM_FPT, 1),
                    ("alarm_oat", False, REG_ALARM_OAT, 1),
                    ("alarm_sat", False, REG_ALARM_SAT, 1),
                    ("alarm_rat", False, REG_ALARM_RAT, 1),
                    ("alarm_eat", False, REG_ALARM_EAT, 1),
                    ("alarm_ect", False, REG_ALARM_ECT, 1),
                    ("alarm_eft", False, REG_ALARM_EFT, 1),
                    ("alarm_oht", False, REG_ALARM_OHT, 1),
                    ("alarm_emt", False, REG_ALARM_EMT, 1),
                    ("alarm_bys", False, REG_ALARM_BYS, 1),
                    ("alarm_sec_air", False, REG_ALARM_SEC_AIR, 1),
                    ("alarm_filter", False, REG_ALARM_FILTER, 1),
                    ("alarm_rh", False, REG_ALARM_RH, 1),
                    ("alarm_low_SAT", False, REG_ALARM_LOW_SAT, 1),
                    ("alarm_pdm_rhs", False, REG_ALARM_PDM_RHS, 1),
                    ("alarm_pdm_eat", False, REG_ALARM_PDM_EAT, 1),
                    ("alarm_man_fan_stop", False, REG_ALARM_MAN_FAN_STOP, 1),
                    ("alarm_overheat_temp", False, REG_ALARM_OVERHEAT_TEMP, 1),
                    ("alarm_fire", False, REG_ALARM_FIRE, 1),
                    ("alarm_filter_warn", False, REG_ALARM_FILTER_WARN, 1),
                    # last: grouped ABC
                    ("alarm_type_abc", False, REG_ALARM_TYPE_A, 3),
                ]
                descriptors.extend(alarm_regs)

            # split descriptors into input & holding lists with stable indices
            input_entries: List[Tuple[int, int, int]] = []
            holding_entries: List[Tuple[int, int, int]] = []
            for idx, (_key, is_input, addr, cnt) in enumerate(descriptors):
                (input_entries if is_input else holding_entries).append((idx, addr, cnt))

            # read both types
            input_results = await self._batch_read_type(input_entries, is_input=True)
            holding_results = await self._batch_read_type(holding_entries, is_input=False)

            # assemble full results list (index -> regs)
            results: List[Optional[List[int]]] = []
            for idx, (_key, is_input, _addr, _cnt) in enumerate(descriptors):
                regs = input_results.get(idx) if is_input else holding_results.get(idx)
                results.append(regs)

            # Now decode into the friendly data dict
            data: Dict[str, Any] = {}

            for idx, (key, is_input, addr, cnt) in enumerate(descriptors):
                regs = results[idx]
                # common short-circuits
                if regs is None:
                    # many sensors we prefer None or 0 depending on semantics
                    if key.startswith("alarm_"):
                        data[key] = 0
                    else:
                        data[key] = None
                    continue

                # decoders
                if key == "mode_main":
                    data["mode_main"] = int(regs[0])
                    continue
                if key == "mode_speed":
                    data["mode_speed"] = int(regs[0])
                    continue
                if key == "target_temp":
                    data["target_temp"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "temp_outdoor":
                    data["temp_outdoor"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "temp_supply":
                    data["temp_supply"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "temp_exhaust":
                    data["temp_exhaust"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "temp_extract":
                    data["temp_extract"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "temp_overheat":
                    data["temp_overheat"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "rpms":
                    data["saf_rpm"] = regs[0] if len(regs) > 0 else None
                    data["eaf_rpm"] = regs[1] if len(regs) > 1 else None
                    continue
                if key == "fan_pcts":
                    data["fan_supply"] = regs[0] if len(regs) > 0 else None
                    data["fan_extract"] = regs[1] if len(regs) > 1 else None
                    continue
                if key == "heater_percentage":
                    data["heater_percentage"] = regs[0]
                    continue
                if key == "heat_exchanger_state":
                    data["heat_exchanger_state"] = regs[0]
                    continue
                if key == "rotor":
                    data["rotor"] = regs[0]
                    continue
                if key == "heater":
                    data["heater"] = regs[0]
                    continue
                if key == "setpoint_eco_offset":
                    data["setpoint_eco_offset"] = round(regs[0] * 0.1, 1)
                    continue
                if key == "mode_summerwinter":
                    data["mode_summerwinter"] = bool(regs[0] > 0)
                    continue
                if key == "fanrun_cool":
                    data["fan_running"] = bool(regs[0] > 0)
                    data["cooldown"] = bool(len(regs) > 1 and regs[1] > 0)
                    continue
                if key == "damper_state":
                    data["damper_state"] = bool(regs[0] > 0)
                    continue
                if key == "cooling_recovery":
                    data["cooling_recovery"] = bool(regs[0] > 0)
                    continue
                if key == "countdown_time_s":
                    data["countdown_time_s"] = regs[0]
                    continue
                if key == "countdown_time_s_factor":
                    data["countdown_time_s_factor"] = regs[0]
                    continue
                if key == "durations":
                    # holiday_days, away_hours, fireplace_mins, refresh_mins, crowded_hours
                    if regs:
                        data["holiday_days"] = regs[0]
                        data["away_hours"] = regs[1] if len(regs) > 1 else None
                        data["fireplace_mins"] = regs[2] if len(regs) > 2 else None
                        data["refresh_mins"] = regs[3] if len(regs) > 3 else None
                        data["crowded_hours"] = regs[4] if len(regs) > 4 else None
                    continue
                if key in ("eco_mode", "heater_enable", "rh_transfer"):
                    data_key = {
                        "eco_mode": "eco_mode",
                        "heater_enable": "heater_enable",
                        "rh_transfer": "rh_transfer",
                    }[key]
                    data[data_key] = bool(regs[0] > 0)
                    continue

                # alarms & ABC
                if key.startswith("alarm_") and key != "alarm_type_abc":
                    data[key] = int(regs[0]) if regs else 0
                    continue
                if key == "alarm_type_abc":
                    # 3 registers payload -> typeA/typeB/typeC
                    data["alarm_typeA"] = int(regs[0]) if len(regs) > 0 else 0
                    data["alarm_typeB"] = int(regs[1]) if len(regs) > 1 else 0
                    data["alarm_typeC"] = int(regs[2]) if len(regs) > 2 else 0
                    continue

            return data

        except Exception as err:
            raise UpdateFailed(f"Coordinator update error: {err}") from err
