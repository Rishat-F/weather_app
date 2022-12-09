"""Getting current GPS coordinates."""

import json
from json.decoder import JSONDecodeError
from typing import NamedTuple

from config import CURRENT_LOCATION_INFO_SERVICE_URL
from exceptions import CantGetGpsCoordinates, CommandExecutionFailed
from shell_command import CURL, CURL_SILENT_ARG, ShellCommand

GET_GPS_COMMAND = ShellCommand(
    executable=CURL,
    arguments=[CURL_SILENT_ARG, CURRENT_LOCATION_INFO_SERVICE_URL],
)


class Coordinates(NamedTuple):
    """GPS coordinates in tuple format."""

    latitude: float
    longitude: float


def get_gps_coordinates() -> Coordinates:
    """Return current GPS coordinates."""
    coordinates = _get_gps_coordinates_by_command(GET_GPS_COMMAND)
    return coordinates


def _get_gps_coordinates_by_command(command: ShellCommand) -> Coordinates:
    """Return GPS coordinates by shell command."""
    try:
        command_output, *_ = command.execute()
    except CommandExecutionFailed as err:
        raise CantGetGpsCoordinates(
            f"Can't get GPS coordinates using "
            f"{[command.executable, *command.arguments]} command.\n"
            f"{err}"
        )
    except UnicodeDecodeError as err:
        raise CantGetGpsCoordinates(f"Can't decode shell command output:\n{err}")
    coordinates = _parse_coordinates(command_output)
    return coordinates


def _parse_coordinates(get_gps_command_output: str) -> Coordinates:
    """Return GPS coordinates from output of shell command."""
    try:
        gps_info = json.loads(get_gps_command_output)
        latitude, longitude = map(float, gps_info["loc"].split(","))
    except KeyError:
        raise CantGetGpsCoordinates(
            f"Shell command output:\n'{get_gps_command_output}'\nhas no dictionary "
            f"with latitude and longitute inside itself"
        )
    except JSONDecodeError:
        raise CantGetGpsCoordinates(
            f"Shell command output:\n'{get_gps_command_output}'\nhas no dictionary "
            f"with latitude and longitute inside itself"
        )
    except ValueError:
        raise CantGetGpsCoordinates(
            f"Shell command output:\n'{get_gps_command_output}'\nhas no dictionary "
            f"with latitude and longitute inside itself"
        )
    return Coordinates(latitude=latitude, longitude=longitude)


if __name__ == "__main__":
    print(get_gps_coordinates())
