"""A command line tool that will generate a storage directory given a configuration."""

import argparse
import pathlib
import sys
import logging


from . import driver

_LOGGER = logging.getLogger(__name__)


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = argparse.ArgumentParser(description="Synthetic Home Storage Driver")
    parser.add_argument(
        "--config",
        type=str,
        help="The yaml configuration file used to generate synthetic data.",
        required=True,
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="The output directory to overwrite with configuration data.",
        required=True,
    )
    arguments = parser.parse_args()
    return arguments


def main():
    """Scaffold an integration."""
    logging.basicConfig(level=logging.DEBUG)

    args = get_arguments()

    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    home_config_path = pathlib.Path(args.config)
    with home_config_path.open() as fd:
        content = fd.read()
        with (output_dir / home_config_path.name).open("w") as out:
            out.write(content)

    driver.Driver(home_config_path.name, output_dir).run_until_complete()

    return 0


if __name__ == "__main__":
    sys.exit(main())
