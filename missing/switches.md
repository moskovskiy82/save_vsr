# Missing Switches

## Configuration Switches
Our integration has: ECO Mode, Heater Enable, RH Transfer
Example integration has additional switches:

- **Free Cooling** - Enable/disable free cooling function
  Register: REG_FREE_COOLING_ON_OFF (4101)
  
- **Manual Fan Stop Allowed** - Allow manual fan stop (safety feature)
  Register: REG_FAN_MANUAL_STOP_ALLOWED (1353)

Note: Our integration already has the most important switches (ECO Mode, Heater Enable, RH Transfer).
The example only adds 2 more switches which are less commonly used features.