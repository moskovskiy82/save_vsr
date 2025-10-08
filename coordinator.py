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

# how long to wait before retrying failed addresses (in polls)
RESET_FAILED_EVERY = 180  # ~30min at 10s interval

# maximum gap for block merging in registers (small gaps tolerated)
MAX_BLOCK_GAP = 2


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
        self._slow_counter = 0  # run slow cycle every N fast polls
        self._poll_count = 0  # for resetting failed addresses
        self._failed_addrs: set[int] = set()
        self._failure_count: int = 0

    async def _batch_read_type(
        self, entries: List[Tuple[int, int, int]], is_input: bool
    ) -> Dict[int, Optional[List[int]]]:
        """
        Do grouped reads for either input or holding registers.
        entries = list of (index, address, count)
        Returns mapping index -> list[int] | None
        """
        if not entries:
            return {}
        entries_sorted = sorted(entries, key=lambda x: x[1])
        blocks: List[dict] = []
        cur_block = None

        for idx, addr, cnt in entries_sorted:
            if addr in self._failed_addrs:
                continue  # Skip known failed addresses
            new_end = addr + cnt - 1
            if cur_block is None:
                cur_block = {"start": addr, "end": new_end, "items": [(idx, addr, cnt)]}
                continue
            # merge blocks if close enough
            if addr <= cur_block["end"] + MAX_BLOCK_GAP + 1:
                cur_block["end"] = max(cur_block["end"], new_end)
                cur_block["items"].append((idx, addr, cnt))
            else:
                blocks.append(cur_block)
                cur_block = {"start": addr, "end": new_end, "items": [(idx, addr, cnt)]}
        if cur_block:
            blocks.append(cur_block)

        results: Dict[int, Optional[List[int]]] = {}
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
                # Mark specific addresses as failed
                for (idx, addr, cnt) in block["items"]:
                    self._failed_addrs.add(addr)
                    results[idx] = None
            else:
                for (idx, addr, cnt) in block["items"]:
                    offset = addr - start
                    part = regs[offset : offset + cnt] if offset + cnt <= len(regs) else regs[offset:]
                    results[idx] = part if part else None

        return results

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            # Preserve previous data to avoid losing slow-cycle values
            data: dict[str, Any] = self.data.copy() if self.data else {}

            # Reset failed addresses periodically to retry
            self._poll_count += 1
            if self._poll_count % RESET_FAILED_EVERY == 0:
                self._failed_addrs.clear()
                _LOGGER.debug("Reset failed addresses for periodic retry")

            # --- build fast descriptors (run every cycle) ---
            descriptors: List[Tuple[bool, int, int]] = [
                (True, REG_MODE_MAIN_STATUS_IN, 1),
                (False, REG_MODE_SPEED, 1),
                (False, REG_TARGET_TEMP, 1),
                (False, REG_TEMP_OUTDOOR, 1),
                (False, REG_TEMP_SUPPLY, 1),
                (False, REG_TEMP_EXHAUST, 1),
                (False, REG_TEMP_EXTRACT, 1),
                (False, REG_TEMP_OVERHEAT, 1),
                (False, REG_SAF_RPM, 2),
                (False, REG_EAF_RPM, 2),
                (False, REG_SUPPLY_FAN_PCT, 2),
                (False, REG_EXTRACT_FAN_PCT, 2),
                (False, REG_HEATER_PERCENT, 1),
                (False, REG_HEAT_EXCH_STATE, 1),
                (False, REG_ROTOR, 1),
                (False, REG_HEATER, 1),
                (False, REG_SETPOINT_ECO_OFFSET, 1),
                (False, REG_MODE_SUMMERWINTER, 1),
                (False, REG_FAN_RUNNING_START, 2),
                (False, REG_DAMPER_STATE, 1),
                (False, REG_COOLING_RECOVERY, 1),
                (True, REG_USERMODE_REMAIN, 1),
                (True, REG_USERMODE_FACTOR, 1),
                (False, REG_HOLIDAY_DAYS, 1),
                (False, REG_AWAY_HOURS, 1),
                (False, REG_FIREPLACE_MINS, 1),
                (False, REG_REFRESH_MINS, 1),
                (False, REG_CROWDED_HOURS, 1),
            ]

            # --- add slow cycle descriptors (alarms + switches) ---
            self._slow_counter += 1
            run_slow = self._slow_counter >= SLOW_CYCLE_EVERY  # every 6 cycles (~60s if fast=10s)
            if self.data is None:
                run_slow = True  # Force slow on first poll
            if run_slow:
                self._slow_counter = 0
                alarms: List[Tuple[bool, int, int]] = [
                    (False, REG_ALARM_SAF, 1),
                    (False, REG_ALARM_EAF, 1),
                    (False, REG_ALARM_FROST_PROT, 1),
                    (False, REG_ALARM_SAF_RPM, 1),
                    (False, REG_ALARM_EAF_RPM, 1),
                    (False, REG_ALARM_FPT, 1),
                    (False, REG_ALARM_OAT, 1),
                    (False, REG_ALARM_SAT, 1),
                    (False, REG_ALARM_RAT, 1),
                    (False, REG_ALARM_EAT, 1),
                    (False, REG_ALARM_ECT, 1),
                    (False, REG_ALARM_EFT, 1),
                    (False, REG_ALARM_OHT, 1),
                    (False, REG_ALARM_EMT, 1),
                    (False, REG_ALARM_BYS, 1),
                    (False, REG_ALARM_SEC_AIR, 1),
                    (False, REG_ALARM_FILTER, 1),
                    (False, REG_ALARM_RH, 1),
                    (False, REG_ALARM_LOW_SAT, 1),
                    (False, REG_ALARM_PDM_RHS, 1),
                    (False, REG_ALARM_PDM_EAT, 1),
                    (False, REG_ALARM_MAN_FAN_STOP, 1),
                    (False, REG_ALARM_OVERHEAT_TEMP, 1),
                    (False, REG_ALARM_FIRE, 1),
                    (False, REG_ALARM_FILTER_WARN, 1),
                    (False, REG_ALARM_TYPE_A, 3),
                ]
                if REG_ECO_MODE_ENABLE is not None:
                    alarms.append((False, REG_ECO_MODE_ENABLE, 1))
                if REG_HEATER_ENABLE is not None:
                    alarms.append((False, REG_HEATER_ENABLE, 1))
                if REG_RH_TRANSFER_ENABLE is not None:
                    alarms.append((False, REG_RH_TRANSFER_ENABLE, 1))

                descriptors.extend(alarms)

            # --- split into input vs holding ---
            input_entries: List[Tuple[int, int, int]] = []
            holding_entries: List[Tuple[int, int, int]] = []
            for i, (is_input, addr, cnt) in enumerate(descriptors):
                (input_entries if is_input else holding_entries).append((i, addr, cnt))

            input_results = await self._batch_read_type(input_entries, is_input=True)
            holding_results = await self._batch_read_type(holding_entries, is_input=False)

            results: List[Optional[List[int]]] = []
            for i, (is_input, _addr, _cnt) in enumerate(descriptors):
                results.append(input_results.get(i) if is_input else holding_results.get(i))

            # Track failures for individual descriptors
            for i, res in enumerate(results):
                if res is None:
                    failed_addr = descriptors[i][1]  # addr
                    self._failed_addrs.add(failed_addr)
                    _LOGGER.debug("Failed to read register at %s; skipping in future polls", failed_addr)

            # --- unpack ---
            (
                mode_main_in,
                mode_speed,
                target_temp,
                t_oat,
                t_sat,
                t_eat,
                t_extract,
                t_oht,
                rpms_saf,
                rpms_eaf,
                fan_pcts_supply,
                fan_pcts_extract,
                heater_pct,
                exch_state,
                rotor,
                heater,
                eco_offs,
                summerwinter,
                fanrun_cool,
                damper,
                cool_recovery,
                cdown_s,
                cdown_factor,
                holiday_days,
                away_hours,
                fireplace_mins,
                refresh_mins,
                crowded_hours,
                *maybe_alarms,
            ) = results + [None] * (len(descriptors) - len(results))  # Pad if fewer

            # decode fast stuff
            data["mode_main"] = mode_main_in[0] if mode_main_in else None
            data["mode_speed"] = mode_speed[0] if mode_speed else None
            data["target_temp"] = round((target_temp[0] if target_temp else 0) * 0.1, 1)
            data["temp_outdoor"] = round((t_oat[0] if t_oat else 0) * 0.1, 1)
            data["temp_supply"] = round((t_sat[0] if t_sat else 0) * 0.1, 1)
            data["temp_exhaust"] = round((t_eat[0] if t_eat else 0) * 0.1, 1)
            data["temp_extract"] = round((t_extract[0] if t_extract else 0) * 0.1, 1)
            data["temp_overheat"] = round((t_oht[0] if t_oht else 0) * 0.1, 1)

            data["saf_rpm"] = rpms_saf[0] if rpms_saf else None
            data["eaf_rpm"] = rpms_eaf[0] if rpms_eaf else None
            data["fan_supply"] = fan_pcts_supply[0] if fan_pcts_supply else None
            data["fan_extract"] = fan_pcts_extract[0] if fan_pcts_extract else None
            data["heater_percentage"] = heater_pct[0] if heater_pct else None
            data["heat_exchanger_state"] = exch_state[0] if exch_state else None
            data["rotor"] = rotor[0] if rotor else None
            data["heater"] = heater[0] if heater else None
            data["setpoint_eco_offset"] = round((eco_offs[0] if eco_offs else 0) * 0.1, 1)

            data["mode_summerwinter"] = bool(summerwinter and summerwinter[0] > 0)
            data["fan_running"] = bool(fanrun_cool and fanrun_cool[0] > 0)
            data["cooldown"] = bool(fanrun_cool and len(fanrun_cool) > 1 and fanrun_cool[1] > 0)
            data["damper_state"] = bool(damper and damper[0] > 0)
            data["cooling_recovery"] = bool(cool_recovery and cool_recovery[0] > 0)

            data["countdown_time_s"] = cdown_s[0] if cdown_s else 0
            data["countdown_time_s_factor"] = cdown_factor[0] if cdown_factor else 0

            data["holiday_days"] = holiday_days[0] if holiday_days else None
            data["away_hours"] = away_hours[0] if away_hours else None
            data["fireplace_mins"] = fireplace_mins[0] if fireplace_mins else None
            data["refresh_mins"] = refresh_mins[0] if refresh_mins else None
            data["crowded_hours"] = crowded_hours[0] if crowded_hours else None

            # decode alarms + switches only if in slow cycle
            if run_slow and maybe_alarms:
                alarm_regs = maybe_alarms[:26]  # 25 singles + 1 triple
                switch_regs = maybe_alarms[26:]  # up to 3 switches
                alarm_keys = [
                    "alarm_saf", "alarm_eaf", "alarm_frost_protect", "alarm_saf_rpm",
                    "alarm_eaf_rpm", "alarm_fpt", "alarm_oat", "alarm_sat", "alarm_rat",
                    "alarm_eat", "alarm_ect", "alarm_eft", "alarm_oht", "alarm_emt",
                    "alarm_bys", "alarm_sec_air", "alarm_filter", "alarm_rh", "alarm_low_SAT",
                    "alarm_pdm_rhs", "alarm_pdm_eat", "alarm_man_fan_stop", "alarm_overheat_temp",
                    "alarm_fire", "alarm_filter_warn",
                ]
                for key, reg in zip(alarm_keys, alarm_regs[:25]):
                    data[key] = reg[0] if reg else 0

                type_abc = alarm_regs[25] if len(alarm_regs) > 25 else None
                data["alarm_typeA"] = type_abc[0] if type_abc else 0
                data["alarm_typeB"] = type_abc[1] if type_abc and len(type_abc) > 1 else 0
                data["alarm_typeC"] = type_abc[2] if type_abc and len(type_abc) > 2 else 0

                switch_idx = 0
                if REG_ECO_MODE_ENABLE is not None:
                    eco = switch_regs[switch_idx] if switch_idx < len(switch_regs) else None
                    data["eco_mode"] = bool(eco and eco[0] > 0)
                    switch_idx += 1
                if REG_HEATER_ENABLE is not None:
                    heater_en = switch_regs[switch_idx] if switch_idx < len(switch_regs) else None
                    data["heater_enable"] = bool(heater_en and heater_en[0] > 0)
                    switch_idx += 1
                if REG_RH_TRANSFER_ENABLE is not None:
                    rh = switch_regs[switch_idx] if switch_idx < len(switch_regs) else None
                    data["rh_transfer"] = bool(rh and rh[0] > 0)

            # Add diagnostics
            data["modbus_failures"] = self._failure_count

            return data

        except Exception as err:
            raise UpdateFailed(f"Coordinator update error: {err}") from err
