Not really working yet. Crahes after some time

Custom integration for save vsr units. Serial and TCP?
Tested on the VSR 500 connected via USB modbus connector.

1. Temporary disable you modbus config by commenting it out from HA config file
2. Create and copy all the files from this repo into you config/custom_components/save_vsr directory
3. Restart HA
4. Go to Settings, Devices and Integrations and add Systemair VSR
5. Enter the details for connection
6. Test
7. Post to issues any problems you encounter

Integration was created completely with the aid of AI tools by someone who dowsn't know python. But somehow it works )

## Branding

This integration uses the domain `save_vsr` to avoid conflicts with other Systemair integrations. The integration icon/logo is managed through the [Home Assistant brands repository](https://github.com/home-assistant/brands).

**Note:** Local PNG files (icon.png, logo.png) are not used by Home Assistant for integration cards. To add custom branding:
1. Create a Pull Request to the [brands repository](https://github.com/home-assistant/brands)
2. Add your logos under `custom_integrations/save_vsr/`
3. Follow the [contribution guidelines](https://github.com/home-assistant/brands/blob/master/CONTRIBUTING.md)

Until then, the integration will use Home Assistant's default icon.
