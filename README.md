# homeassistant-airzone
Home Assistant Custom component to manage Aironze installations.
It relays on the [python-airzone](https://pypi.org/project/python-airzone/) library to connect to a Innobus / Airzone installation.

The current code is compatible with the new HA Climate 1.0.
To use it in HA add it to the configuration.yml:
```
climate:
  - platform: airzone
    host: ip_of_airzone_gateway 
    port: 5020
```
For a proper configuration of the gateway please take a look to the [python-airzone](https://pypi.org/project/python-airzone/) library.

This component discover automatically the Machines and Zones associated to them. 
As HA doens't provide (yet) a proper generic way to handle multiroom / multizones HVAC with a centralized machine, this component creates a climate device for each Machine that interfaces with the Machine state (STOP-AIR-COOL-HOT-HOTPLUS etc...) and a climate device for each of the zones to control them.
Ideally each zone would include the machine control (that is global to all zones on the machine) to avoid having two climate devices for each zone / group.
