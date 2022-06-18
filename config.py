"""Configurations of the application."""

from enum import Enum


class OpenWeatherLanguage(Enum):
    """
    Languages supported on Open Weather API Service.

    Here only few of them.
    List of all supported langs -> https://openweathermap.org/current#multi
    """

    ENGLISH = "en"
    RUSSIAN = "ru"


USE_ROUNDED_COORDS = True
