"""Tests for application exceptions."""

import pytest

from exceptions import CantGetGpsCoordinates, CommandRunsTooLong, NoSuchCommand


@pytest.mark.xfail(reason="not realized yet")
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
