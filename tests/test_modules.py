"""Tests for application modules."""

import numbers
import sys
from datetime import datetime
from io import StringIO
from typing import Any

import pytest
from pytest import MonkeyPatch

from config import SpeedUnit, TemperatureUnit
from converters import (
    convert_to_fahrenheit,
    convert_to_kelvin,
    convert_to_kph,
    convert_to_mph,
)
from coordinates import Coordinates, get_gps_coordinates
from weather import main
from weather_api_service import Weather, WeatherType, get_weather, Celsius, Kelvin, Fahrenheit
from weather_formatter import format_weather


class TestGettingGpsCoordinates:
    """Tests for coordinates.py module."""

    def setup_method(self) -> None:
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

    def setup_method(self) -> None:
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


class TestFormattingWeather:
    """Tests for weather_formatter.py module."""

    def test_weather_formatter(self) -> None:
        """False test."""
        weather = Weather(
            temperature=15,
            weather_type=WeatherType.CLOUDS,
            weather_description="Переменная облачность",
            wind_speed=2.5,
            sunrise=datetime.fromisoformat("2022-05-03 04:00:00"),
            sunset=datetime.fromisoformat("2022-05-03 20:25:14"),
            city="moscow",
        )
        expected_displaying_weather = (
            "Moscow, 15°C, Облачно\n\nПеременная облачность\n"
            "Ветер: 2.5m/s\nВосход: 04:00\nЗакат: 20:25\n"
        )
        actual_displaying_weather = format_weather(weather)
        assert expected_displaying_weather == actual_displaying_weather


class TestDisplayingWeather:
    """Check that programm really display weather in terminal."""

    def test_display_weather(self, monkeypatch: MonkeyPatch) -> None:
        """Check weather printing."""

        def mock_get_gps_coordinates() -> None:
            """Mock get_coordinates function."""
            return None

        def mock_get_weather(_: Any) -> Weather:
            """Mock get_weather function."""
            weather = Weather(
                temperature=15,
                weather_type=WeatherType.CLOUDS,
                weather_description="Переменная облачность",
                wind_speed=2.5,
                sunrise=datetime.fromisoformat("2022-05-03 04:00:00"),
                sunset=datetime.fromisoformat("2022-05-03 20:25:14"),
                city="moscow",
            )
            return weather

        mock_io = StringIO()
        monkeypatch.setattr("sys.stdout", mock_io)
        monkeypatch.setattr("weather.get_gps_coordinates", mock_get_gps_coordinates)
        monkeypatch.setattr("weather.get_weather", mock_get_weather)
        main()
        expected_displaying_weather = (
            "Moscow, 15°C, Облачно\n\nПеременная облачность\n"
            "Ветер: 2.5m/s\nВосход: 04:00\nЗакат: 20:25\n\n"
        )
        assert sys.stdout.getvalue() == expected_displaying_weather  # type: ignore


class TestConverters:
    """Tests for converters.py module."""

    @pytest.mark.parametrize(
        "temperature_celsius,temperature_kelvin",
        [
            (0, 273),
            (-273, 0),
        ],
    )
    def test_convert_to_kelvin(self, temperature_celsius: Celsius, temperature_kelvin: Kelvin) -> None:
        """Test converting temperature from °C to °K."""
        assert convert_to_kelvin(temperature_celcius) == temperature_kelvin

    @pytest.mark.parametrize(
        "temperature_celsius,temperature_fahrenheit",
        [
            (-10, 14),
            (-1, 30),
            (0, 32),
            (16, 61),
        ],
    )
    def test_convert_to_fahrenheit(self, temperature_celsius: Celsius, temperature_fahrenheit: Fahrenheit) -> None:
        """Test converting temperature from °C to °F."""
        assert convert_to_fahrenheit(temperature_celsius) == temperature_fahrenheit

    @pytest.mark.parametrize(
        "speed_mps, speed_kmph",
        [
            (0.0, 0.0),
            (1.0, 3.6),
            (1.88, 6.8),
            (3.123, 11.2),
            (5, 18.0),
            (10.0, 36.0),
        ],
    )
    def test_convert_to_kph(self, speed_mps: Meters_per_second, speed_kmph: Kilometers_per_hour) -> None:
        """Test converting speed from m/s to km/h."""
        assert convert_to_kph(speed_mps) == speed_kmph

    @pytest.mark.parametrize(
        "speed_mps, speed_mph",
        [
            (0.0, 0.0),
            (1.0, 2.2),
            (2, 4.5),
            (3.55, 7.9),
            (6.442, 14.4),
            (10.0, 22.4),
        ],
    )
    def test_convert_to_mph(self, speed_mps: Meters_per_second, speed_mph: Miles_per_hour) -> None:
        """Test converting speed from m/s to mph."""
        assert convert_to_mph(speed_mps) == speed_mph

class TestConfigs:
    """Tests for config.py module."""

    def setup_method(self) -> None:
        """Setup for all tests."""  # noqa
        self.weather = Weather(
            temperature=15,
            weather_type=WeatherType.CLOUDS,
            weather_description="Переменная облачность",
            wind_speed=2.5,
            sunrise=datetime.fromisoformat("2022-05-03 04:00:00"),
            sunset=datetime.fromisoformat("2022-05-03 20:25:14"),
            city="Moscow",
        )

    @pytest.mark.xfail(reason="test not realized yet", run=False)
    def test_ru_language(self) -> None:
        """Test Open Weather API service work with lang=ru config."""
        assert False

    @pytest.mark.xfail(reason="test not realized yet", run=False)
    def test_en_language(self) -> None:
        """Test Open Weather API service work with lang=en config."""
        assert False

    @pytest.mark.parametrize(
        "temperature_unit,expected_temperature",
        [
            (TemperatureUnit.CELSIUS, "15°C"),
            (TemperatureUnit.KELVIN, "288°K"),
            (TemperatureUnit.FAHRENHEIT, "59°F"),
        ],
    )
    def test_temperature_unit(
        self,
        monkeypatch: MonkeyPatch,
        temperature_unit: TemperatureUnit,
        expected_temperature: str,
    ) -> None:
        """Test weather displaying in/with configured temperature unit."""
        monkeypatch.setattr("config.TEMPERATURE_UNIT", temperature_unit)
        assert expected_temperature in format_weather(self.weather)

    @pytest.mark.parametrize(
        "speed_unit,expected_speed",
        [
            (SpeedUnit.METERS_PER_SECOND, "2.5m/s"),
            (SpeedUnit.KILOMETERS_PER_HOUR, "9.0km/h"),
            (SpeedUnit.MILES_PER_HOUR, "5.6mph"),
        ],
    )
    def test_speed_unit(
        self,
        monkeypatch: MonkeyPatch,
        speed_unit: SpeedUnit,
        expected_speed: str,
    ) -> None:
        """Test weather displaying in/with configured speed unit."""
        monkeypatch.setattr("config.SPEED_UNIT", speed_unit)
        assert expected_speed in format_weather(self.weather)

    @pytest.mark.parametrize(
        "weather_displaying_pattern, expected_displaying_weather",
        [
            (
                (
                    "{city}\n{temperature}{temperature_unit}, {weather_type}\n\n"
                    "Ветер: {wind_speed}{speed_unit}\n"
                    "Восход: {sunrise}\n"
                    "Закат: {sunset}\n"
                ),
                (
                    "Moscow\n15°C, Облачно\n\n"
                    "Ветер: 2.5m/s\n"
                    "Восход: 04:00\n"
                    "Закат: 20:25\n"
                ),
            ),
            (
                "{city}\n{temperature}{temperature_unit}, {weather_type}\n\n",
                "Moscow\n15°C, Облачно\n\n",
            ),
        ],
    )
    def test_different_weather_displayings(
        self,
        monkeypatch: MonkeyPatch,
        weather_displaying_pattern: str,
        expected_displaying_weather: str,
    ) -> None:
        """Test different weather displaying patterns."""
        monkeypatch.setattr(
            "weather_formatter.WEATHER_DISPLAYING_PATTERN", weather_displaying_pattern
        )
        actual_displaying_weather = format_weather(self.weather)
        assert actual_displaying_weather == expected_displaying_weather
