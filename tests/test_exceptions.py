"""Tests for application exceptions."""

from subprocess import Popen
from typing import Any

import pytest
from pytest import MonkeyPatch

import config
import shell_command
from coordinates import Coordinates
from exceptions import (
    ApiServiceError,
    CantGetGpsCoordinates,
    CantGetWeather,
    CommandRunsTooLong,
    NoOpenWeatherApiKey,
    NoSuchCommand,
)
from shell_command import ShellCommand
from weather_api_service import get_weather

Undecodable_bytes = bytes


@pytest.mark.xfail(reason="test not realized yet", run=False)
class TestCoordinatesModuleExceptions:
    """Test exceptions raising while getting current GPS coordinates."""

    def test_no_such_command(self) -> None:
        """There is no command in system for getting current GPS coordinates."""
        assert isinstance(False, NoSuchCommand)

    def test_command_runs_too_long(self) -> None:
        """Command for getting current GPS coordinates runs too long."""
        assert isinstance(False, CommandRunsTooLong)

    def test_command_has_stderr(self) -> None:
        """Command for getting current GPS coordinates ends with err in stderr."""
        assert isinstance(False, CantGetGpsCoordinates)

    def test_command_has_wrong_exit_code(self) -> None:
        """Command for getting current GPS coordinates returns code != 0."""
        assert isinstance(False, CantGetGpsCoordinates)

    def test_undecodable_command_output(self) -> None:
        """Command stdout is undecodable."""
        assert isinstance(False, CantGetGpsCoordinates)

    def test_command_output_has_no_lat_lon_dictionary(self) -> None:
        """Command stdout has no dictionary with latitude and longitude."""
        assert isinstance(False, CantGetGpsCoordinates)

    def test_command_output_has_incorrect_dictionary(self) -> None:
        """
        Dictionary with latitude and longitude is incorrect for json.loads().

        Example: '{'latitude': 50.55, 'longitude': 50.55, qwerty}'.
        """
        assert isinstance(False, CantGetGpsCoordinates)


class TestWeatherApiServiceExceptions:
    """Test exceptions raising while getting weather by GPS coordinates."""

    coordinates = Coordinates(latitude=50, longitude=50)

    def test_no_such_command(self, monkeypatch: MonkeyPatch) -> None:
        """There is no command in system for getting weather by GPS coordinates."""

        class MonkeyPatchShellCommand(ShellCommand):
            def __init__(self, *args: Any, **kwargs: Any):
                _, _ = args, kwargs
                self.executable = "qwerty"
                self.arguments = []
                self.timeout = 1

        monkeypatch.setattr(shell_command, "ShellCommand", MonkeyPatchShellCommand)
        with pytest.raises(NoSuchCommand):
            get_weather(self.coordinates)

    def test_no_open_weather_api_key(self, monkeypatch: MonkeyPatch) -> None:
        """There is no OPEN_WEATHER_API_KEY variable in your environment."""
        monkeypatch.setattr(config, "OPEN_WEATHER_API_KEY", None)
        with pytest.raises(NoOpenWeatherApiKey):
            get_weather(self.coordinates)

    def test_command_runs_too_long(self, monkeypatch: MonkeyPatch) -> None:
        """Command for getting weather by GPS coordinates runs too long."""

        class MonkeyPatchShellCommand(ShellCommand):
            """Mock for ShellCommand __init__ method."""

            def __init__(self, **_: Any):
                self.executable = "ping"
                self.arguments = ["google.com"]
                self.timeout = 0.5

        monkeypatch.setattr(shell_command, "ShellCommand", MonkeyPatchShellCommand)
        with pytest.raises(CommandRunsTooLong):
            get_weather(self.coordinates)

    def test_wrong_open_weather_api_key(self, monkeypatch: MonkeyPatch) -> None:
        """There is wrong OPEN_WEATHER_API_KEY variable in your environment."""
        monkeypatch.setattr(config, "OPEN_WEATHER_API_KEY", "qwerty")
        with pytest.raises(ApiServiceError):
            get_weather(self.coordinates)

    def test_command_has_stderr(self, monkeypatch: MonkeyPatch) -> None:
        """Command for getting weather by GPS coordinates ends with err in stderr."""

        def monkeypatch_communicate(*args: Any, **kwargs: Any) -> tuple[Any, bytes]:
            """Mock for Popen.communicate method."""
            _, _ = args, kwargs
            return (None, b"error")

        monkeypatch.setattr(Popen, "communicate", monkeypatch_communicate)
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    def test_command_has_wrong_exit_code(self, monkeypatch: MonkeyPatch) -> None:
        """Command for getting weather by GPS coordinates returns code != 0."""

        def monkeypatch_wait(*args: Any, **kwargs: Any) -> int:
            """Mock for Popen.wait method."""
            _, _ = args, kwargs
            return 1

        monkeypatch.setattr(Popen, "wait", monkeypatch_wait)
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    def test_undecodable_command_output(self, monkeypatch: MonkeyPatch) -> None:
        """Command stdout is undecodable."""
        undecodable_bytes = b"\x80\x02\x03"

        def monkeypatch_communicate(
            *args: Any, **kwargs: Any
        ) -> tuple[Undecodable_bytes, Any]:
            _, _ = args, kwargs
            return (undecodable_bytes, None)

        monkeypatch.setattr(Popen, "communicate", monkeypatch_communicate)
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    @pytest.mark.parametrize(
        "command_output",
        [
            "Output without dictionary",
            "Output without dictionary: {broken dictionary]",
            "Output without dictionary: {'also': 'broken', dictionary, 'a': '1'}",
            "Output without dictionary: {'broken': 'dictionary', 'too': ''}}",
            "{'also': 'broken', dictionary, 'a': '1'}",
        ],
    )
    def test_command_output_has_incorrect_dictionary(
        self, command_output: str, monkeypatch: MonkeyPatch
    ) -> None:
        """Command stdout has no dictionary inside."""

        def monkeypatch_execute(*args: Any, **kwargs: Any) -> tuple[str, Any, Any]:
            """Mock for ShellCommand execute method."""
            _, _ = args, kwargs
            return (command_output, None, None)

        monkeypatch.setattr(ShellCommand, "execute", monkeypatch_execute)
        with pytest.raises(CantGetWeather):
            get_weather(self.coordinates)

    @pytest.mark.parametrize(
        "command_output",
        [
            '{"weather":[{"id":800,"description":"ясно"}],"main":{}, \
                "wind":{"speed":3},"sys":{"sunrise":1656115279, \
                "sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"description":"ясно"}],"main":{"temp":20.29}, \
                "wind":{"speed":3},"sys":{"sunrise":1656115279, \
                "sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800}],"main":{"temp":20.29}, \
                "wind":{"speed":3},"sys":{"sunrise":1656115279, \
                "sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], \
                "main":{"temp":20.29},"wind":{},"sys":{"sunrise":1656115279, \
                "sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], \
                "main":{"temp":20.29},"wind":{"speed":3}, \
                "sys":{"sunset":1656178205},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], \
                "main":{"temp":20.29},"wind":{"speed":3}, \
                "sys":{"sunrise":1656115279},"name":"малые кабаны"}',
            '{"weather":[{"id":800,"description":"ясно"}], \
                "main":{"temp":20.29},"wind":{"speed":3}, \
                "sys":{"sunrise":1656115279,"sunset":1656178205}}',
            'Invalid dictionary: {"invalid": "dictionary"}',
            "{}",
        ],
    )
    def test_command_output_has_invalid_dictionary(
        self, command_output: str, monkeypatch: MonkeyPatch
    ) -> None:
        """Command stdout has dictionary without needed weather data."""

        def monkeypatch_execute(*args: Any, **kwargs: Any) -> tuple[str, Any, Any]:
            """Mock for ShellCommand execute method."""
            _, _ = args, kwargs
            return (command_output, None, None)

        monkeypatch.setattr(ShellCommand, "execute", monkeypatch_execute)
        with pytest.raises(ApiServiceError):
            get_weather(self.coordinates)
