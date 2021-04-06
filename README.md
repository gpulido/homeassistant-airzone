# homeassistant-airzone
Home Assistant Custom component to manage Aironze installations.
It relays on the [python-airzone](https://pypi.org/project/python-airzone/) library to connect to a Innobus / Airzone installation.

Currently it supports Innobus and Aidoo installations.

The current code is compatible with the new HA Climate 1.0.

## Installation and Configuration

In order to use it, the airzone folder should be placed under the config/custom_components of the HA installation.
The component has two ways of configuring it:

### 1) Using the configuration.yml

To use it in HA add it to the configuration.yml:

```
climate:
  - platform: airzone
    host: ip_of_airzone_gateway 
    port: 5020
    device_id: 1 # the Innobus machine address id / Aidoo slave id
    device_class: 'innobus' # 'aido' for the aidoo integration
```

### 2) Integrations menu

The component provide a integration workflow that could be used for configuration instead of the yml.

Goto configuration -> Integrations -> Add integration

![alt text](screenshots/airzone_integration.png?raw=true "Integration")

For a proper configuration of the gateway please take a look to the [python-airzone](https://pypi.org/project/python-airzone/) library.


## Innobus

Given an Innobus MachineID, this component  discover automatically the Zones associated to them. 
As HA doesn't provide (yet) a proper generic way to handle multiroom / multizones HVAC with a centralized machine, this component creates a climate device for each Machine that interfaces with the Machine state (STOP-AIR-COOL-HOT-HOTPLUS etc...) and a climate device for each of the zones to control them.

Example of climate card as Innobus Machine: 

![alt text](screenshots/innobus_machine.png?raw=true "Innobus Machine")

Example of climate card as Innobus Zone:

![alt text](screenshots/innobus_zone.png?raw=true "Innobus Zone")

Ideally each zone would include the machine control (that is global to all zones on the machine) to avoid having two climate devices for each zone / group.


