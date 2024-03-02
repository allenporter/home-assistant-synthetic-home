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
    - name: Family Room
      device_type: hvac
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
  Master Bedroom:
    - name: Bedroom Light
      device_type: light-dimmable
    - name: Bedroom Blinds
      device_type: smart-blinds
    - name: Bedroom Window
      device_type: window-sensor
  Garage:
    - name: Garage Door
      device_type: garage-door
  Front Yard:
    - name: Front motion
      device_type: motion-sensor
```

You can generate a Home Assistant `config/` directory that is setup with the
synthetic home integration:

```bash
$ export PYTHONPATH="${PYTHONPATH}:${PWD}/custom_components"
$ python3 -m script.storage --config farmhouse.yaml --output_dir=config/
```

This creates the `config/` directory and you can then start up home assistant:

```bash
$ hass -c connfig/
```

And it will create all the synthetic devices for you:

![Screenshot](synthetic_home.png)
