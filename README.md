# Synthetic Home

This is Home Assistant custom component that generates a synthetic home from a
configuration file, used for testing.

## Synthetic Home Configuration

See `custom_components/synthetic_home/model.py` for a description of the configuration
file format. This is essentially modeled after Home Assistants `demo` platform
but allows you to name devices and stick them in areas using a configuration file.

## Synthetic Home Generation

Given an example synthetic home configuration file `farmhouse.yaml`:

```yaml
---
name: Family Farmhouse
device_entities:
  Family Room:
    - name: Family Room Lamp
      device_type: light
      device_info:
        manufacturer: Phillips
        model: Hue
    - name: Family Room
      device_type: hvac
      device_info:
        manufacturer: Nest
        sw_version: 1.0.0
    - name: Left Window
      device_type: window-sensor
    - name: Right Window
      device_type: window-sensor
  Entry:
    - name: Front Door
      device_type: smart-lock
  Kitchen:
    - name: Light
      device_type: light-dimmable
    - name: Coffe Maker
      device_type: smart-plug
      device_info:
        manufacturer: Shelly
  Master Bedroom:
    - name: Bedroom Light
      device_type: light-dimmable
    - name: Bedroom Blinds
      device_type: smart-blinds
      device_info:
        model: RollerBlinds
        manufacturer: Motion Blinds
        sw_version: 1.1.0
    - name: Bedroom Window
      device_type: window-sensor
  Garage:
    - name: Garage Door
      device_type: garage-door
  Front Yard:
    - name: Front motion
      device_type: motion-sensor
```

---
name: Family Farmhouse
device_entities:
  Family room:
  - name: Family room
    device_type: heat-pump
    unique_id: d4df546410f90f1c1d9be6a8443b8ec6
    device_info:
      model: Thermostat
      manufacturer: Nest
      sw_version: 1.0.0
    attributes:
      unit_of_measurement: °F
      current_temperature: 60


You can generate a Home Assistant `config/` directory that is setup with the
synthetic home integration:

```bash
$ export PYTHONPATH="${PYTHONPATH}:${PWD}/custom_components"
$ python3 -m script.storage --config farmhouse.yaml --output_dir=config/
```

This creates the `config/` directory and you can then start up home assistant:

```bash
$ hass -c config/
```

And it will create all the synthetic devices for you:

![Screenshot](synthetic_home.png)

## Manual Creation

You can also add Synthetic Home like a normal integration. During the configuration
flow you specify a yaml file like `farmhouse.yaml` and it expects to find it in your
`config/` folder next to `configuration.yaml`. (This is similar above, and the same
step the storage generation tool is doing internally).

## Testing

See `tests/` for examples of how to create a synthetic devices in your tests
using `pytest-homeassistant-custom-component`.
