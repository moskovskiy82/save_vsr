from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

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
    REG_ALARM_TYPE_B,
    REG_ALARM_TYPE_C,
)
from .hub import VSRHub

_LOGGER = logging.getLogger(__name__)

class VSRCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, hub: VSRHub, update_interval_s: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Systemair VSR Coordinator",
            update_interval=timedelta(seconds=update_interval_s or DEFAULT_UPDATE_INTERVAL),
        )
        self.hub = hub

    async def _async_update_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        try:
            # The reads are grouped to limit round-trips.
            # 1) Modes / temperatures / % / RPMs / misc
            tasks = [
                self.hub.read_input(REG_MODE_MAIN_STATUS_IN, 1),
                self.hub.read_holding(REG_MODE_SPEED, 1),
                self.hub.read_holding(REG_TARGET_TEMP, 1),
                self.hub.read_holding(REG_TEMP_OUTDOOR, 1),
                self.hub.read_holding(REG_TEMP_SUPPLY, 1),
                self.hub.read_holding(REG_TEMP_EXHAUST, 1),
                self.hub.read_holding(REG_TEMP_EXTRACT, 1),
                self.hub.read_holding(REG_TEMP_OVERHEAT, 1),
                self.hub.read_holding(REG_SAF_RPM, 2),  # SAF/EAF
                self.hub.read_holding(REG_SUPPLY_FAN_PCT, 2),
                self.hub.read_holding(REG_HEATER_PERCENT, 1),
                self.hub.read_holding(REG_HEAT_EXCH_STATE, 1),
                self.hub.read_holding(REG_ROTOR, 1),
                self.hub.read_holding(REG_HEATER, 1),
                self.hub.read_holding(REG_SETPOINT_ECO_OFFSET, 1),
                self.hub.read_holding(REG_MODE_SUMMERWINTER, 1),
                self.hub.read_holding(REG_FAN_RUNNING_START, 2),
                self.hub.read_holding(REG_DAMPER_STATE, 1),
                self.hub.read_holding(REG_COOLING_RECOVERY, 1),
                # timers
                self.hub.read_input(REG_USERMODE_REMAIN, 1),
                self.hub.read_input(REG_USERMODE_FACTOR, 1),
                # durations
                self.hub.read_holding(REG_HOLIDAY_DAYS, 5),
                # alarms (sampled individually; could be more batched if continuous)
                self.hub.read_holding(REG_ALARM_SAF, 1),
                self.hub.read_holding(REG_ALARM_EAF, 1),
                self.hub.read_holding(REG_ALARM_FROST_PROT, 1),
                self.hub.read_holding(REG_ALARM_SAF_RPM, 1),
                self.hub.read_holding(REG_ALARM_EAF_RPM, 1),
                self.hub.read_holding(REG_ALARM_FPT, 1),
                self.hub.read_holding(REG_ALARM_OAT, 1),
                self.hub.read_holding(REG_ALARM_SAT, 1),
                self.hub.read_holding(REG_ALARM_RAT, 1),
                self.hub.read_holding(REG_ALARM_EAT, 1),
                self.hub.read_holding(REG_ALARM_ECT, 1),
                self.hub.read_holding(REG_ALARM_EFT, 1),
                self.hub.read_holding(REG_ALARM_OHT, 1),
                self.hub.read_holding(REG_ALARM_EMT, 1),
                self.hub.read_holding(REG_ALARM_BYS, 1),
                self.hub.read_holding(REG_ALARM_SEC_AIR, 1),
                self.hub.read_holding(REG_ALARM_FILTER, 1),
                self.hub.read_holding(REG_ALARM_RH, 1),
                self.hub.read_holding(REG_ALARM_LOW_SAT, 1),
                self.hub.read_holding(REG_ALARM_PDM_RHS, 1),
                self.hub.read_holding(REG_ALARM_PDM_EAT, 1),
                self.hub.read_holding(REG_ALARM_MAN_FAN_STOP, 1),
                self.hub.read_holding(REG_ALARM_OVERHEAT_TEMP, 1),
                self.hub.read_holding(REG_ALARM_FIRE, 1),
                self.hub.read_holding(REG_ALARM_FILTER_WARN, 1),
                self.hub.read_holding(REG_ALARM_TYPE_A, 3),
            ]
            (
                mode_main_in,
                mode_speed,
                target_temp,
                t_oat, t_sat, t_eat, t_rat, t_oht,
                rpms, fan_pcts,
                heater_pct, exch_state, rotor, heater,
                eco_offs, summerwinter, fanrun_cool, damper, cool_recovery,
                cdown_s, cdown_factor,
                durations,  # 5 regs
                *alarms,
            ) = await asyncio.gather(*tasks)

            # decode basic
            data["mode_main"] = mode_main_in[0] if mode_main_in else None
            data["mode_speed"] = mode_speed[0] if mode_speed else None
            data["target_temp"] = round((target_temp[0] if target_temp else 0) * 0.1, 1)

            data["temp_outdoor"] = round((t_oat[0] if t_oat else 0) * 0.1, 1)
            data["temp_supply"] = round((t_sat[0] if t_sat else 0) * 0.1, 1)
            data["temp_exhaust"] = round((t_eat[0] if t_eat else 0) * 0.1, 1)
            data["temp_extract"] = round((t_rat[0] if t_rat else 0) * 0.1, 1)
            data["temp_overheat"] = round((t_oht[0] if t_oht else 0) * 0.1, 1)

            data["saf_rpm"] = rpms[0] if rpms else None
            data["eaf_rpm"] = rpms[1] if rpms and len(rpms) > 1 else None

            data["fan_supply"] = fan_pcts[0] if fan_pcts else None
            data["fan_extract"] = fan_pcts[1] if fan_pcts and len(fan_pcts) > 1 else None

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

            if durations:
                data["holiday_days"]   = durations[0]
                data["away_hours"]     = durations[1]
                data["fireplace_mins"] = durations[2]
                data["refresh_mins"]   = durations[3]
                data["crowded_hours"]  = durations[4]

            # alarms decoding as ints (0..3 where applicable)
            alarm_keys = [
                "alarm_saf","alarm_eaf","alarm_frost_protect","alarm_saf_rpm",
                "alarm_eaf_rpm","alarm_fpt","alarm_oat","alarm_sat","alarm_rat",
                "alarm_eat","alarm_ect","alarm_eft","alarm_oht","alarm_emt",
                "alarm_bys","alarm_sec_air","alarm_filter","alarm_rh","alarm_low_SAT",
                "alarm_pdm_rhs","alarm_pdm_eat","alarm_man_fan_stop","alarm_overheat_temp",
                "alarm_fire","alarm_filter_warn",
            ]
            for key, reg in zip(alarm_keys, alarms[:-1]):  # last alarms[-1] are type A/B/C tuple
                data[key] = (reg[0] if reg else 0)

            type_abc = alarms[-1] if alarms else None
            data["alarm_typeA"] = type_abc[0] if type_abc else 0
            data["alarm_typeB"] = type_abc[1] if type_abc and len(type_abc) > 1 else 0
            data["alarm_typeC"] = type_abc[2] if type_abc and len(type_abc) > 2 else 0

            return data

        except Exception as err:
            raise UpdateFailed(f"Coordinator update error: {err}") from err
