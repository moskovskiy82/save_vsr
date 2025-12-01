# Systemair SAVE VSR Integration

Custom Home Assistant integration for Systemair SAVE VSR ventilation units via Modbus RTU (RS485).

**Status:** Active development - tested on VSR 500 with USB Modbus connector

## Features

- **Climate Control:** Full HVAC control with preset modes (Auto, Manual, Fireplace, etc.)
- **Temperature Sensors:** Outdoor, Supply, Exhaust, Overheat temperatures
- **Fan Monitoring:** RPM and percentage for both supply and extract fans
- **Power Monitoring:** Real-time power consumption for fans and heater
- **Energy Dashboard:** Native energy sensors for Home Assistant Energy Dashboard
  - **Fans Energy:** Combined energy consumption of supply + extract fans
  - **Heater Energy:** Separate heater energy consumption
- **Alarms:** Comprehensive alarm monitoring (frost protection, filters, sensors, etc.)
- **Countdown Timers:** Remaining time for temporary modes (Away, Fireplace, etc.)

## Installation

1. Temporarily disable any existing Modbus config in your HA configuration
2. Copy all files from this repo to `config/custom_components/save_vsr/`
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Systemair VSR" and configure your connection
6. Test and report any issues

## Energy Dashboard Setup

The integration provides two energy sensors compatible with Home Assistant's Energy Dashboard:

1. **Fans Energy** (`sensor.vsr_fans_energy`)
   - Tracks combined energy consumption of supply and extract fans
   - Replaces generic power calculation tools for ventilation unit

2. **Heater Energy** (`sensor.vsr_heater_energy`)
   - Tracks heater energy consumption separately
   - Useful for analyzing heating costs

### Adding to Energy Dashboard:

1. Go to Settings → Dashboards → Energy
2. Click "Add Consumption"
3. Select `sensor.vsr_fans_energy` and/or `sensor.vsr_heater_energy`
4. Energy data will accumulate automatically and persist across restarts

## Technical Details

- **Protocol:** Modbus RTU over RS485
- **Library:** pymodbus (async)
- **Update Interval:** 30 seconds (configurable)
- **Energy Calculation:** Real-time power integration with state restoration
- **Supported Models:** VSR 500 (other models may work but untested)

## Branding

This integration uses the domain `save_vsr` to avoid conflicts with other Systemair integrations. The integration icon/logo is managed through the [Home Assistant brands repository](https://github.com/home-assistant/brands).

**Note:** Local PNG files (icon.png, logo.png) are not used by Home Assistant for integration cards. To add custom branding:
1. Create a Pull Request to the [brands repository](https://github.com/home-assistant/brands)
2. Add your logos under `custom_integrations/save_vsr/`
3. Follow the [contribution guidelines](https://github.com/home-assistant/brands/blob/master/CONTRIBUTING.md)

Until then, the integration will use Home Assistant's default icon.

## Development

Integration created with AI assistance. Contributions welcome!
