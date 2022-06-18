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

USE_ROUNDED_COORDS = True
