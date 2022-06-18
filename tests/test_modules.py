"""Tests for application modules."""

import numbers

import pytest

from coordinates import Coordinates, get_gps_coordinates


@pytest.mark.xfail(reason="Getting current GPS coordinates dont work yet.")
class TestGettingGpsCoordinates:
    """Tests for coordinates.py module."""

    def setup(self) -> None:
        """Setup for all tests."""  # noqa
        self.coordinates = get_gps_coordinates()

    def test_get_gps_coordinates_returns_coordinates(self) -> None:
        """Check get_gps_coordinates returns Coordinates type."""
        assert isinstance(self.coordinates, Coordinates)

    def test_coordinates_has_latitude_and_longitude(self) -> None:
        """Check coordinates has latitude and longitude attributes."""
        assert hasattr(self.coordinates, "latitude")
        assert hasattr(self.coordinates, "longitude")

    def test_coordinates_latitude_and_longitude_are_numbers(self) -> None:
        """Check latitude and longitude are numbers."""
        assert isinstance(self.coordinates.latitude, numbers.Real)
        assert isinstance(self.coordinates.longitude, numbers.Real)
