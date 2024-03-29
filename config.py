"""Configurations of the application."""

import os
from enum import Enum


class OpenWeatherLanguage(Enum):
    """
    Languages supported on Open Weather API Service.

    Here only few of them.
    List of all supported langs -> https://openweathermap.org/current#multi
    """

    ENGLISH = "en"
    RUSSIAN = "ru"


class TemperatureUnit(Enum):
    """Temperature measurement unit."""

    CELSIUS = "°C"
    KELVIN = "°K"
    FAHRENHEIT = "°F"


class SpeedUnit(Enum):
    """Speed measurement unit."""

    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    MILES_PER_HOUR = "mph"


OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY", default=None)
CURRENT_LOCATION_INFO_SERVICE_URL = "https://ipinfo.io/json"

open_weather_api_lang = OpenWeatherLanguage.RUSSIAN
temperature_unit = TemperatureUnit.CELSIUS
speed_unit = SpeedUnit.METERS_PER_SECOND
