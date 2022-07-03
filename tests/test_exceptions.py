"""Tests for application exceptions."""

from subprocess import Popen
from typing import Any, Callable, Type

import pytest
from pytest import MonkeyPatch

import config
import shell_command
from coordinates import Coordinates, get_gps_coordinates
from exceptions import (
    ApiServiceError,
    CantGetGpsCoordinates,
    CantGetWeather,
    CommandRunsTooLong,
    NoInternetConnection,
    NoOpenWeatherApiKey,
    NoSuchCommand,
)
from shell_command import ShellCommand
from weather_api_service import get_weather

Undecodable_bytes = bytes
Exit_code = int
NO_INTERNET_EXIT_CODE = 100


@pytest.fixture
def not_existing_command() -> Type[ShellCommand]:
    """Fixture for not existing shell command."""

    class MonkeyPatchShellCommand(ShellCommand):
        """Mock for ShellCommand.__init__ method."""

        def __init__(self, *args: Any, **kwargs: Any):
            _, _ = args, kwargs
            self.executable = "qwerty"
            self.arguments = []
            self.timeout = 1

    return MonkeyPatchShellCommand


@pytest.fixture
def long_running_command() -> Type[ShellCommand]:
    """Fixture for long running shell command."""

    class MonkeyPatchShellCommand(ShellCommand):
        """Mock for ShellCommand.__init__ method."""

        def __init__(self, *args: Any, **kwargs: Any):
            _, _ = args, kwargs
            self.executable = "ping"
            self.arguments = ["localhost"]
            self.timeout = 0.5

    return MonkeyPatchShellCommand


@pytest.fixture
def usual_command() -> Type[ShellCommand]:
    """Fixture for usual shell command."""

    class MonkeyPatchShellCommand(ShellCommand):
        """Mock for ShellCommand.__init__ method."""

        def __init__(self, *args: Any, **kwargs: Any):
            _, _ = args, kwargs
            self.executable = "echo"
            self.arguments = []
            self.timeout = 0.5
            self.no_internet_exit_code = None

    return MonkeyPatchShellCommand


@pytest.fixture
def command_that_use_internet() -> Type[ShellCommand]:
    """Fixture for shell command that use internet."""

    class MonkeyPatchShellCommand(ShellCommand):
        """Mock for ShellCommand.__init__ method."""

        def __init__(self, *args: Any, **kwargs: Any):
            _, _ = args, kwargs
            self.executable = "echo"
            self.arguments = []
            self.timeout = 0.5
            self.no_internet_exit_code = NO_INTERNET_EXIT_CODE

    return MonkeyPatchShellCommand


@pytest.fixture
def monkeypatch_communicate_with_stderr() -> Callable[[Any, Any], tuple[Any, bytes]]:
    """Mock for Popen.communicate method that returns stderr."""

    def inner(*args: Any, **kwargs: Any) -> tuple[Any, bytes]:
        _, _ = args, kwargs
        return (None, b"error")

    return inner


@pytest.fixture
def monkeypatch_communicate_with_undecodable_output() -> Callable[
    [Any, Any], tuple[Undecodable_bytes, Any]
]:
    """Mock for Popen.communicate method."""

    def inner(*args: Any, **kwargs: Any) -> tuple[Undecodable_bytes, Any]:
        _, _ = args, kwargs
        undecodable_bytes = b"\x80\x02\x03"
        return (undecodable_bytes, None)

    return inner


@pytest.fixture
def monkeypatch_wait() -> Callable[[Exit_code], Callable[[Any, Any], Exit_code]]:
    """Mock for Popen.wait method that returns needed exit code."""

    def inner(exit_code: Exit_code) -> Callable[[Any, Any], Exit_code]:
        def inner_in_inner(*args: Any, **kwargs: Any) -> Exit_code:
            _, _ = args, kwargs
            return exit_code

        return inner_in_inner

    return inner


@pytest.fixture
def monkeypatch_execute() -> Callable[
    [str], Callable[[Any, Any], tuple[str, Any, Any]]
]:
    """Mock for ShellCommand.execute method."""

    def inner(command_output: str) -> Callable[[Any, Any], tuple[str, Any, Any]]:
        def inner_in_inner(*args: Any, **kwargs: Any) -> tuple[str, Any, Any]:
            _, _ = args, kwargs
            return (command_output, None, None)

        return inner_in_inner

    return inner


class TestCoordinatesModuleExceptions:
    """Test exceptions raising while getting current GPS coordinates."""

    def test_no_such_command(
        self,
        monkeypatch: MonkeyPatch,
        not_existing_command: Callable[[], Type[ShellCommand]],
    ) -> None:
        """If there is no command in system for getting current GPS coordinates."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", not_existing_command())
        with pytest.raises(NoSuchCommand):
            get_gps_coordinates()

    def test_no_internet(
        self,
        monkeypatch: MonkeyPatch,
        command_that_use_internet: Callable[[], Type[ShellCommand]],
        monkeypatch_wait: Callable[[Exit_code], Callable[[Any, Any], Exit_code]],
    ) -> None:
        """If there is no internet connection."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", command_that_use_internet())
        monkeypatch.setattr(Popen, "wait", monkeypatch_wait(NO_INTERNET_EXIT_CODE))
        with pytest.raises(NoInternetConnection):
            get_gps_coordinates()

    def test_command_runs_too_long(
        self,
        monkeypatch: MonkeyPatch,
        long_running_command: Callable[[], Type[ShellCommand]],
    ) -> None:
        """If command for getting current GPS coordinates runs too long."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", long_running_command())
        with pytest.raises(CommandRunsTooLong):
            get_gps_coordinates()

    def test_command_has_stderr(
        self,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_communicate_with_stderr: Callable[
            [], Callable[[Any, Any], tuple[Any, bytes]]
        ],
    ) -> None:
        """If command for getting current GPS coordinates ends with err in stderr."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", usual_command())
        monkeypatch.setattr(Popen, "communicate", monkeypatch_communicate_with_stderr)
        with pytest.raises(CantGetGpsCoordinates):
            get_gps_coordinates()

    def test_command_has_wrong_exit_code(
        self,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_wait: Callable[[Exit_code], Callable[[Any, Any], Exit_code]],
    ) -> None:
        """If command for getting current GPS coordinates returns code != 0."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", usual_command())
        monkeypatch.setattr(Popen, "wait", monkeypatch_wait(NO_INTERNET_EXIT_CODE))
        with pytest.raises(CantGetGpsCoordinates):
            get_gps_coordinates()

    def test_undecodable_command_output(
        self,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_communicate_with_undecodable_output: Callable[
            [Any, Any], tuple[Undecodable_bytes, Any]
        ],
    ) -> None:
        """If command stdout is undecodable."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", usual_command())
        monkeypatch.setattr(
            Popen, "communicate", monkeypatch_communicate_with_undecodable_output
        )
        with pytest.raises(CantGetGpsCoordinates):
            get_gps_coordinates()

    @pytest.mark.xfail(reason="right regex in _parse_coordinates not realized yet")
    @pytest.mark.parametrize(
        "command_output",
        [
            '{"latitude": 50}',
            '{"longitude": 50}',
            '{"latitude": 50, "longitud": 50}',
            '{"latitud": 50, "longitude": 50}',
            '{"latitud": 50, "longitud": 50}',
            'Invalid dictionary: {"invalid": "dictionary"}',
            "{}",
        ],
    )
    def test_command_output_has_no_lat_lon_dictionary(
        self,
        command_output: str,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_execute: Callable[
            [str], Callable[[Any, Any], tuple[str, Any, Any]]
        ],
    ) -> None:
        """If command stdout has no dictionary with latitude and longitude."""
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", usual_command())
        monkeypatch.setattr(
            ShellCommand, "execute", monkeypatch_execute(command_output)
        )
        with pytest.raises(CantGetGpsCoordinates):
            get_gps_coordinates()

    @pytest.mark.parametrize(
        "command_output",
        [
            '{"latitude": 50, "longitude": 50, qwerty}',
            '{qwerty "latitude": 50, "longitude": 50}',
            '{"latitude": 50, qwerty, "longitude": 50}',
            '{qwerty "latitude": 50, "longitude": 50 qwerty}',
            '{"latitude": lat, "longitude": 50}',
            '{"latitude": 50, "longitude": lon}',
        ],
    )
    def test_command_output_has_incorrect_dictionary(
        self,
        command_output: str,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_execute: Callable[
            [str], Callable[[Any, Any], tuple[str, Any, Any]]
        ],
    ) -> None:
        """
        If dictionary with latitude and longitude is incorrect for json.loads().

        Example: '{'latitude': 50.55, 'longitude': 50.55, qwerty}'.
        """
        monkeypatch.setattr("coordinates.GET_GPS_COMMAND", usual_command())
        monkeypatch.setattr(
            ShellCommand, "execute", monkeypatch_execute(command_output)
        )
        with pytest.raises(CantGetGpsCoordinates):
            get_gps_coordinates()


class TestWeatherApiServiceExceptions:
    """Test exceptions raising while getting weather by GPS coordinates."""

    coordinates = Coordinates(latitude=50, longitude=50)

    def test_no_such_command(
        self,
        monkeypatch: MonkeyPatch,
        not_existing_command: Callable[[], Type[ShellCommand]],
    ) -> None:
        """If there is no command in system for getting weather by GPS coordinates."""
        monkeypatch.setattr(shell_command, "ShellCommand", not_existing_command)
        with pytest.raises(NoSuchCommand):
            get_weather(self.coordinates)

    def test_no_internet(
        self,
        monkeypatch: MonkeyPatch,
        command_that_use_internet: Callable[[], Type[ShellCommand]],
        monkeypatch_wait: Callable[[Exit_code], Callable[[Any, Any], Exit_code]],
    ) -> None:
        """If there is no internet connection."""
        monkeypatch.setattr(shell_command, "ShellCommand", command_that_use_internet)
        monkeypatch.setattr(Popen, "wait", monkeypatch_wait(NO_INTERNET_EXIT_CODE))
        with pytest.raises(NoInternetConnection):
            get_weather(self.coordinates)

    def test_no_open_weather_api_key(self, monkeypatch: MonkeyPatch) -> None:
        """If there is no OPEN_WEATHER_API_KEY variable in your environment."""
        monkeypatch.setattr(config, "OPEN_WEATHER_API_KEY", None)
        with pytest.raises(NoOpenWeatherApiKey):
            get_weather(self.coordinates)

    def test_command_runs_too_long(
        self,
        monkeypatch: MonkeyPatch,
        long_running_command: Callable[[], Type[ShellCommand]],
    ) -> None:
        """If command for getting weather by GPS coordinates runs too long."""
        monkeypatch.setattr(shell_command, "ShellCommand", long_running_command)
        with pytest.raises(CommandRunsTooLong):
            get_weather(self.coordinates)

    def test_wrong_open_weather_api_key(self, monkeypatch: MonkeyPatch) -> None:
        """If there is wrong OPEN_WEATHER_API_KEY variable in your environment."""
        monkeypatch.setattr(config, "OPEN_WEATHER_API_KEY", "qwerty")
        with pytest.raises(ApiServiceError):
            get_weather(self.coordinates)

    def test_command_has_stderr(
        self,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_communicate_with_stderr: Callable[
            [], Callable[[Any, Any], tuple[Any, bytes]]
        ],
    ) -> None:
        """If command for getting weather by GPS coordinates ends with err in stderr."""
        monkeypatch.setattr(shell_command, "ShellCommand", usual_command)
        monkeypatch.setattr(Popen, "communicate", monkeypatch_communicate_with_stderr)
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    def test_command_has_wrong_exit_code(
        self,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_wait: Callable[[Exit_code], Callable[[Any, Any], Exit_code]],
    ) -> None:
        """If command for getting weather by GPS coordinates returns code != 0."""
        monkeypatch.setattr(shell_command, "ShellCommand", usual_command)
        monkeypatch.setattr(Popen, "wait", monkeypatch_wait(NO_INTERNET_EXIT_CODE))
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    def test_undecodable_command_output(
        self,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_communicate_with_undecodable_output: Callable[
            [Any, Any], tuple[Undecodable_bytes, Any]
        ],
    ) -> None:
        """If command stdout is undecodable."""
        monkeypatch.setattr(shell_command, "ShellCommand", usual_command)
        monkeypatch.setattr(
            Popen, "communicate", monkeypatch_communicate_with_undecodable_output
        )
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    @pytest.mark.parametrize(
        "command_output",
        [
            "Output without dictionary",
            "Output without dictionary: {broken dictionary]",
            'Output without dictionary: {"also": "broken", dictionary, "a": "1"}',
            'Output without dictionary: {"broken": "dictionary", "too": ""}}',
            '{"also": "broken", dictionary, "a": "1"}',
        ],
    )
    def test_command_output_has_incorrect_dictionary(
        self,
        command_output: str,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_execute: Callable[
            [str], Callable[[Any, Any], tuple[str, Any, Any]]
        ],
    ) -> None:
        """If command stdout has no dictionary inside."""
        monkeypatch.setattr(shell_command, "ShellCommand", usual_command)
        monkeypatch.setattr(
            ShellCommand, "execute", monkeypatch_execute(command_output)
        )
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    @pytest.mark.parametrize(
        "command_output",
        [
            '{"weather":[{"id":800,"description":"ясно"}],"main":{}, '
            '"wind":{"speed":3},"sys":{"sunrise":1656115279, '
            '"sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"description":"ясно"}],"main":{"temp":20.29}, '
            '"wind":{"speed":3},"sys":{"sunrise":1656115279, '
            '"sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800}],"main":{"temp":20.29}, '
            '"wind":{"speed":3},"sys":{"sunrise":1656115279, '
            '"sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], '
            '"main":{"temp":20.29},"wind":{},"sys":{"sunrise":1656115279, '
            '"sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], '
            '"main":{"temp":20.29},"wind":{"speed":3}, '
            '"sys":{"sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], '
            '"main":{"temp":20.29},"wind":{"speed":3}, '
            '"sys":{"sunrise":1656115279},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], '
            '"main":{"temp":20.29},"wind":{"speed":3}, '
            '"sys":{"sunrise":1656115279,"sunset":1656178205}}',
            'Invalid dictionary: {"invalid": "dictionary"}',
            "{}",
        ],
    )
    def test_command_output_has_invalid_dictionary(
        self,
        command_output: str,
        monkeypatch: MonkeyPatch,
        usual_command: Callable[[], Type[ShellCommand]],
        monkeypatch_execute: Callable[
            [str], Callable[[Any, Any], tuple[str, Any, Any]]
        ],
    ) -> None:
        """If command stdout has dictionary without needed weather data."""
        monkeypatch.setattr(shell_command, "ShellCommand", usual_command)
        monkeypatch.setattr(
            ShellCommand, "execute", monkeypatch_execute(command_output)
        )
        with pytest.raises(ApiServiceError):
            get_weather(self.coordinates)
