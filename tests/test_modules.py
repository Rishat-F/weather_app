"""Tests for application modules."""

import numbers
import sys
from datetime import datetime
from io import StringIO
from typing import Any

import pytest
from pytest import MonkeyPatch

import config
from config import SpeedUnit, TemperatureUnit
from converters import (
    convert_to_fahrenheit,
    convert_to_kelvin,
    convert_to_kph,
    convert_to_mph,
)
from coordinates import Coordinates, get_gps_coordinates
from weather import main
from weather_api_service import (
    Celsius,
    Fahrenheit,
    Kelvin,
    Kilometers_per_hour,
    Meters_per_second,
    Miles_per_hour,
    Weather,
    WeatherType,
    get_weather,
)
from weather_formatter import format_weather


class SetupWeather:
    """Create weather for tests."""

    TEMPERATURE = 15
    WEATHER_TYPE = WeatherType.CLOUDS
    WEATHER_DESCRIPTION = "Переменная облачность"
    WIND_SPEED = 2.5
    SUNRISE = datetime.fromisoformat("2022-05-03 04:00:00")
    SUNSET = datetime.fromisoformat("2022-05-03 20:25:14")
    CITY = "moscow"

    TEST_WEATHER = Weather(
        temperature=TEMPERATURE,
        weather_type=WEATHER_TYPE,
        weather_description=WEATHER_DESCRIPTION,
        wind_speed=WIND_SPEED,
        sunrise=SUNRISE,
        sunset=SUNSET,
        city=CITY,
    )
    EXPECTED_DISPLAYING_WEATHER = (
        f"{CITY.title()}, {TEMPERATURE}{config.TEMPERATURE_UNIT.value}, "
        f"{WEATHER_TYPE.value}\n\n{WEATHER_DESCRIPTION}\n"
        f"Ветер: {WIND_SPEED}{config.SPEED_UNIT.value}\n"
        f"Восход: {SUNRISE.strftime('%H:%M')}\n"
        f"Закат: {SUNSET.strftime('%H:%M')}\n"
    )


class TestGettingGpsCoordinates:
    """Tests for coordinates.py module."""

    @classmethod
    def setup_class(cls) -> None:
        """Setup for all tests."""  # noqa
        cls.coordinates = get_gps_coordinates()

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

    @classmethod
    def setup_class(cls) -> None:
        """Setup for all tests."""  # noqa
        coordinates = Coordinates(latitude=55.75, longitude=52.43)
        cls.weather = get_weather(coordinates)

    def test_get_weather_returns_weather(self) -> None:
        """Check get_weather returns Weather type."""
        assert isinstance(self.weather, Weather)

    @pytest.mark.parametrize(
        "attribute",
        [
            "temperature",
            "weather_type",
            "weather_description",
            "wind_speed",
            "sunrise",
            "sunset",
            "city",
        ],
    )
    def test_weather_has_right_attributes(self, attribute: str) -> None:
        """Check weather has next attributes.

        temperature, weather_type, weather_description,
        wind_speed, sunrise, sunset, city
        """
        assert hasattr(self.weather, attribute)

    @pytest.mark.parametrize(
        "weather_attr,type_",
        [
            ("temperature", numbers.Real),
            ("weather_type", WeatherType),
            ("weather_description", str),
            ("wind_speed", numbers.Real),
            ("sunrise", datetime),
            ("sunset", datetime),
            ("city", str),
        ],
    )
    def test_weather_attributes_types(self, weather_attr: str, type_: Any) -> None:
        """Check weather attributes has right types."""
        assert isinstance(getattr(self.weather, weather_attr), type_)


class TestFormattingWeather(SetupWeather):
    """Tests for weather_formatter.py module."""

    def test_weather_formatter(self) -> None:
        """False test."""
        actual_displaying_weather = format_weather(self.TEST_WEATHER)
        assert actual_displaying_weather == self.EXPECTED_DISPLAYING_WEATHER


class TestDisplayingWeather(SetupWeather):
    """Check that programm really display weather in terminal."""

    def test_display_weather(self, monkeypatch: MonkeyPatch) -> None:
        """Check weather printing."""

        def mock_get_gps_coordinates() -> None:
            """Mock get_coordinates function."""
            return None

        def mock_get_weather(_: Any) -> Weather:
            """Mock get_weather function."""
            return self.TEST_WEATHER

        mock_io = StringIO()
        monkeypatch.setattr("sys.stdout", mock_io)
        monkeypatch.setattr("weather.get_gps_coordinates", mock_get_gps_coordinates)
        monkeypatch.setattr("weather.get_weather", mock_get_weather)
        main()
        assert (
            sys.stdout.getvalue()
            == self.EXPECTED_DISPLAYING_WEATHER + "\n"  # type: ignore
        )


class TestConverters:
    """Tests for converters.py module."""

    @pytest.mark.parametrize(
        "temperature_celsius,temperature_kelvin",
        [
            (0, 273),
            (-273, 0),
        ],
    )
    def test_convert_to_kelvin(
        self, temperature_celsius: Celsius, temperature_kelvin: Kelvin
    ) -> None:
        """Test converting temperature from °C to °K."""
        assert convert_to_kelvin(temperature_celsius) == temperature_kelvin

    @pytest.mark.parametrize(
        "temperature_celsius,temperature_fahrenheit",
        [
            (-10, 14),
            (-1, 30),
            (0, 32),
            (16, 61),
        ],
    )
    def test_convert_to_fahrenheit(
        self, temperature_celsius: Celsius, temperature_fahrenheit: Fahrenheit
    ) -> None:
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
    def test_convert_to_kph(
        self, speed_mps: Meters_per_second, speed_kmph: Kilometers_per_hour
    ) -> None:
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
    def test_convert_to_mph(
        self, speed_mps: Meters_per_second, speed_mph: Miles_per_hour
    ) -> None:
        """Test converting speed from m/s to mph."""
        assert convert_to_mph(speed_mps) == speed_mph


class TestConfigs(SetupWeather):
    """Tests for config.py module."""

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
        assert expected_temperature in format_weather(self.TEST_WEATHER)

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
        assert expected_speed in format_weather(self.TEST_WEATHER)

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
        actual_displaying_weather = format_weather(self.TEST_WEATHER)
        assert actual_displaying_weather == expected_displaying_weather
