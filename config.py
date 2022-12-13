"""Configurations of the application."""

import os
import warnings
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
OPEN_WEATHER_API_LANG = OpenWeatherLanguage.RUSSIAN
OPEN_WEATHER_API_URL_PATTERN = (
    "https://api.openweathermap.org/data/2.5/weather?"
    "lat={latitude}&"
    "lon={longitude}&"
    "appid={api_key}&"
    "lang={language}&"
    "units=metric"
)

TEMPERATURE_UNIT = TemperatureUnit.CELSIUS
SPEED_UNIT = SpeedUnit.METERS_PER_SECOND

match TEMPERATURE_UNIT:
    case TemperatureUnit(name="CELSIUS" | "KELVIN" | "FAHRENHEIT"):
        pass
    case _:
        warnings.warn(
            f"No such option for TEMPERATURE_UNIT: '{TEMPERATURE_UNIT}'. "
            f"Available measurement units for temperature are "
            f"{[unit for unit in TemperatureUnit]}. Temperature shown in °C."
        )
        TEMPERATURE_UNIT = TemperatureUnit.CELSIUS

match SPEED_UNIT:
    case SpeedUnit(name="METERS_PER_SECOND" | "KILOMETERS_PER_HOUR" | "MILES_PER_HOUR"):
        pass
    case _:
        warnings.warn(
            f"No such option for SPEED_UNIT: '{SPEED_UNIT}'. "
            f"Available measurement units for speed are "
            f"{[unit for unit in SpeedUnit]}. Speed shown in m/s."
        )
        SPEED_UNIT = SpeedUnit.METERS_PER_SECOND

match OPEN_WEATHER_API_LANG:
    case OpenWeatherLanguage(name="RUSSIAN" | "ENGLISH"):
        pass
    case _:
        warnings.warn(
            f"No such option for OPEN_WEATHER_API_LANG: '{OPEN_WEATHER_API_LANG}'. "
            f"Available languages are {[language for language in OpenWeatherLanguage]}."
        )
        OPEN_WEATHER_API_LANG = OpenWeatherLanguage.RUSSIAN


WEATHER_DISPLAYING_PATTERN = (
    "{city}, {temperature}{temperature_unit}, {weather_type}\n\n"
    "{weather_description}\n"
    "Ветер: {wind_speed}{speed_unit}\n"
    "Восход: {sunrise}\n"
    "Закат: {sunset}\n"
)

CURRENT_LOCATION_INFO_SERVICE_URL = "https://ipinfo.io/json"
