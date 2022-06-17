"""Getting current GPS coordinates."""

import json
import re
from json.decoder import JSONDecodeError
from subprocess import PIPE, Popen, TimeoutExpired
from typing import List, NamedTuple

import config
from exceptions import CantGetGpsCoordinates, CommandRunsTooLong, NoSuchCommand


class GetGpsCommand(NamedTuple):
    """Shell command for getting current GPS coordinates."""

    executable: str
    args: List[str]


GET_GPS_COMMAND = GetGpsCommand(executable="whereami", args=["-f", "json"])
COMMAND_TIMEOUT = 5


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
    command_output = _get_command_output(command)
    coordinates = _parse_coordinates(command_output)
    return coordinates


def _get_command_output(command: GetGpsCommand) -> bytes:
    """Return output of a shell command."""
    try:
        process = Popen(args=[command.executable, *command.args], stdout=PIPE)
    except FileNotFoundError:
        raise NoSuchCommand(f"There's no command '{command.executable}' in your system")
    try:
        (output, err) = process.communicate(timeout=COMMAND_TIMEOUT)
        exit_code = process.wait(timeout=COMMAND_TIMEOUT)
    except TimeoutExpired as err:
        process.kill()
        raise CommandRunsTooLong(
            f"Command '{err.cmd}' runs more than {err.timeout} seconds"
        )
    if err is not None or exit_code != 0:
        raise CantGetGpsCoordinates(
            f"Can't get GPS coordinates using {process.args} command"  # type: ignore
        )
    return output


def _parse_coordinates(command_output: bytes) -> Coordinates:
    """Return coordinates from output of shell command."""
    try:
        output = command_output.decode().strip().lower()
    except UnicodeDecodeError as err:
        raise CantGetGpsCoordinates(f"Can't decode shell command output:\n{err}")
    dictionary_pattern = r"{.*}"
    try:
        dictionary = json.loads(
            re.search(dictionary_pattern, output).group()  # type: ignore
        )
    except (AttributeError, JSONDecodeError):
        raise CantGetGpsCoordinates(
            f"Shell command output:\n'{output}'\nhas not dictionary inside"
        )
    try:
        return Coordinates(
            latitude=dictionary["latitude"], longitude=dictionary["longitude"]
        )
    except KeyError:
        raise CantGetGpsCoordinates(
            f"There is no 'latitude' and 'longitude' keys inside dictionary "
            f"in shell command output:\n'{output}'"
        )


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
