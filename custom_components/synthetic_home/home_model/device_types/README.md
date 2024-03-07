# Device Type Registry

A device type is a definition of a type of physical device in a smart home. A
device may additionally be represented by multiple entities. For example, a
climate-hvac device may be represented by a climage entity and a temperature
sensor entity.

## Device types

Device types are defined to represent common configured household devices,
but may not support every single feature in the smart home. That is, these
are meant to be representative, but not necessarily exhaustive.

Each file in this directory contains a device type name. New device types
may be added as new use cases are needed.

## Entities

Entities are specified by platform, where each value is an entity description
key defined in the code. That is, adding a new enttiy type requires adding a
new entity description.

## Supported Attributes

A device type can have attributes like 'unit_of_measure' or 'native_value' that
can vary for any specific device that is configured. However, a device
is represented by multiple entities. Therefore we define `supported_attributes`
at the device level and a mapping to `supported_attributes` on each entity. By
default the device attribute will be mapped to entity attributes with the same
name, or the attribute value can map with a key value pair like `native_value=current_temperature`
that maps the device attribute `current_temperature` to the entities
`native_value`.
