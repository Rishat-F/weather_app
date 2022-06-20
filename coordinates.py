"""Getting current GPS coordinates."""

from typing import NamedTuple

import config
from exceptions import CantGetGpsCoordinates, CommandExecutionFailed
from shell_commands import GetGpsCommand

GET_GPS_COMMAND = GetGpsCommand(executable="whereami", arguments=["-f", "json"])


class Coordinates(NamedTuple):
    """GPS coordinates in tuple format."""

    latitude: float
    longitude: float


def get_gps_coordinates() -> Coordinates:
    """Return current GPS coordinates."""
    coordinates = _get_gps_coordinates_by_command(GET_GPS_COMMAND)
    return _round_coordinates(coordinates, 2)


def _get_gps_coordinates_by_command(command: GetGpsCommand) -> Coordinates:
    """Return GPS coordinates by shell command."""
    try:
        command_output, *_ = command.execute()
    except CommandExecutionFailed as err:
        raise CantGetGpsCoordinates(
            f"Can't get GPS coordinates using "
            f"{[command.executable, *command.arguments]} command.\n"
            f"{err}"
        )
    coordinates = command.parse_coordinates(command_output)
    return coordinates


def _round_coordinates(coordinates: Coordinates, ndigit: int = 4) -> Coordinates:
    """Round GPS coordinates to a given precision in decimal digits."""
    if not config.USE_ROUNDED_COORDS:
        return coordinates
    return Coordinates(
        *map(
            lambda coord: round(coord, ndigit),
            [coordinates.latitude, coordinates.longitude],
        )
    )


if __name__ == "__main__":
    print(get_gps_coordinates())
