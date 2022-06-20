"""Tests for application modules."""

import numbers
from datetime import datetime

import pytest  # type: ignore

from coordinates import Coordinates, get_gps_coordinates
from weather_api_service import Weather, WeatherType, get_weather


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


class TestGettingWeather:
    """Tests for weather_api_service.py module."""

    def setup(self) -> None:
        """Setup for all tests."""  # noqa
        coordinates = Coordinates(latitude=55.75, longitude=52.43)
        self.weather = get_weather(coordinates)

    def test_get_weather_returns_weather(self) -> None:
        """Check get_weather returns Weather type."""
        assert isinstance(self.weather, Weather)

    def test_weather_has_right_attributes(self) -> None:
        """Check weather has next attributes.

        temperature, weather_type, weather_description,
        wind_speed, sunrise, sunset, city
        """
        assert hasattr(self.weather, "temperature")
        assert hasattr(self.weather, "weather_type")
        assert hasattr(self.weather, "weather_description")
        assert hasattr(self.weather, "wind_speed")
        assert hasattr(self.weather, "sunrise")
        assert hasattr(self.weather, "sunset")
        assert hasattr(self.weather, "city")

    def test_weather_attributes_types(self) -> None:
        """Check weather attributes has right types."""
        assert isinstance(self.weather.temperature, numbers.Real)
        assert isinstance(self.weather.weather_type, WeatherType)
        assert isinstance(self.weather.weather_description, str)
        assert isinstance(self.weather.wind_speed, numbers.Real)
        assert isinstance(self.weather.sunrise, datetime)
        assert isinstance(self.weather.sunset, datetime)
        assert isinstance(self.weather.city, str)


@pytest.mark.xfail(reason="not realized yet")
class TestFormattingWeather:
    """Tests for weather_formatter.py module."""

    def setup(self) -> None:
        """Setup for all tests."""  # noqa
        self.weather = Weather(
            temperature=14,
            weather_type=WeatherType.CLOUDS,
            weather_description="Переменная облачность",
            wind_speed=2.5,
            sunrise=datetime.fromisoformat("2022-05-03 04:00:00"),
            sunset=datetime.fromisoformat("2022-05-03 20:25:14"),
            city="Moscow",
        )

    def test_true(self) -> None:
        """False test."""
        assert False
