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
