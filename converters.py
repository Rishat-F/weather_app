"""
Converting weather data in different measure units.

In every scenario of getting weather from any weather API service
weather data should come from weather_api_service.py in metric units:
temperature - °С,
speed - m/s (meters per second),
...
And further in weather_formatter.py weather data should be converted
in needed measure units by converters defined in this module.
"""

from weather_api_service import (
    Celsius,
    Fahrenheit,
    Kelvin,
    Kilometers_per_hour,
    Meters_per_second,
    Miles_per_hour,
)


def convert_to_kelvin(temperature: Celsius) -> Kelvin:
    """Approximately convert temperature from °C to °K."""
    return temperature + 273


def convert_to_fahrenheit(temperature: Celsius) -> Fahrenheit:
    """Approximately convert temperature from °C to °F."""
    return round(temperature * 9 / 5 + 32)


def convert_to_mph(speed: Meters_per_second) -> Miles_per_hour:
    """Convert speed from m/s to mph."""
    return round(speed * 2.237, 1)


def convert_to_kph(speed: Meters_per_second) -> Kilometers_per_hour:
    """Convert speed from m/s to km/h."""
    return round(speed * 3.6, 1)
