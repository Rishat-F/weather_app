"""Shell commands used by application."""

import json
import re
from json.decoder import JSONDecodeError
from subprocess import PIPE, Popen, TimeoutExpired
from typing import List, NamedTuple

from coordinates import Coordinates
from exceptions import CantGetGpsCoordinates, CommandRunsTooLong, NoSuchCommand


class CommandExecutionResult(NamedTuple):
    """Result of shell command execution."""

    stdout_data: bytes
    stderr_data: bytes
    exit_code: int


class ShellCommand:
    """
    Unix shell command.

    Application works like request -> response and
    it's runtime must be as fast as it possible.
    That's why there is a timeout field in this class.
    """

    def __init__(self, executable: str, arguments: List[str] = [], timeout: float = 5):
        """Shell command constructor."""
        self.executable = executable
        self.arguments = arguments
        self.timeout = timeout

    def execute(self) -> CommandExecutionResult:
        """Execute shell command."""
        try:
            process = Popen(args=[self.executable, *self.arguments], stdout=PIPE)
        except FileNotFoundError:
            raise NoSuchCommand(
                f"There's no command '{self.executable}' in your system"
            )
        try:
            (stdout, stderr) = process.communicate(timeout=self.timeout)
            exit_code = process.wait(timeout=self.timeout)
        except TimeoutExpired as err:
            process.kill
            raise CommandRunsTooLong(
                f"Command '{err.cmd}' runs more than {err.timeout} seconds"
            )
        return CommandExecutionResult(
            stdout_data=stdout, stderr_data=stderr, exit_code=exit_code
        )

    def _preprocess_stdout_data(self, stdout_data: bytes) -> str:
        """Decode, strip, lower stdout data."""
        return stdout_data.decode().strip().lower()


class GetGpsCommand(ShellCommand):
    """Shell command for getting current GPS coordinates."""

    # Reqex pattern for dictionary including latitude and longitude inside itself
    lat_lon_dict_pattern = r"{.*}"

    def parse_coordinates(self, get_gps_command_output: bytes) -> Coordinates:
        """Return GPS coordinates from output of shell command."""
        try:
            output = self._preprocess_stdout_data(get_gps_command_output)
        except UnicodeDecodeError as err:
            raise CantGetGpsCoordinates(f"Can't decode shell command output:\n{err}")
        try:
            lat_lon_dict = json.loads(
                re.search(self.lat_lon_dict_pattern, output).group()  # type: ignore
            )
        except (AttributeError, JSONDecodeError):
            raise CantGetGpsCoordinates(
                f"Shell command output:\n'{output}'\nhas no dictionary "
                f"with latitude and longitute inside itself"
            )
        return Coordinates(
            latitude=lat_lon_dict["latitude"], longitude=lat_lon_dict["longitude"]
        )
