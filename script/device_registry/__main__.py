"""A command line tool for interacting with the device registry."""

# ruff: noqa: T201

import argparse
from dataclasses import asdict
import sys
import logging
import yaml

from synthetic_home import device_types

_LOGGER = logging.getLogger(__name__)

DUMP_KEYS = {"device_type", "desc", "supported_attributes"}


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser(description="Synthetic Home Device Registry")
    parser.add_argument(
        "--command",
        choices=["dump"],
        help="The command to perform against the registry",
        required=True,
    )
    arguments = parser.parse_args()
    return arguments


def main():
    """Scaffold an integration."""
    logging.basicConfig(level=logging.DEBUG)

    args = get_arguments()
    if args.command == "dump":
        device_registry = device_types.load_device_type_registry()
        output = []
        device_type_names = list(device_registry.device_types)
        device_type_names.sort()

        for name in device_type_names:
            device_type = device_registry.device_types[name]
            data = asdict(device_type)
            values = {key: data[key] for key in DUMP_KEYS if data.get(key)}
            output.append(values)

        print(yaml.dump(output, sort_keys=False, explicit_start=True))

    return 0


if __name__ == "__main__":
    sys.exit(main())
