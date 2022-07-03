"""Getting weather by GPS coordinates."""

import json
import re
from datetime import datetime
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Dict, List, Literal, NamedTuple, TypedDict

import config
import shell_command
from coordinates import Coordinates
from exceptions import (
    ApiServiceError,
    CantGetWeather,
    CommandExecutionFailed,
    NoOpenWeatherApiKey,
)

Temperature = int
Celsius = Temperature
Kelvin = Temperature
Fahrenheit = Temperature

Speed = float
Meters_per_second = Speed
Miles_per_hour = Speed
Kilometers_per_hour = Speed


COMMAND_EXECUTABLE = "curl"
COMMAND_NO_INTERNET_EXIT_CODE = 6


class OpenWeatherDict(TypedDict):
    """Response of the Open Weather API service."""

    weather: List[Dict[Literal["id", "description"], int | str]]
    main: Dict[Literal["temp"], float]
    wind: Dict[Literal["speed"], float]
    sys: Dict[Literal["sunrise", "sunset"], int]
    name: str


class WeatherType(Enum):
    """Weather types presented on Open Weather API service."""

    THUNDERSTORM = "Гроза"
    DRIZZLE = "Изморозь"
    RAIN = "Дождь"
    SNOW = "Снег"
    MIST = "Мгла"
    SMOKE = "Дым"
    HAZE = "Туман"
    DUST = "Пыль"
    FOG = "Туман"
    SAND = "Песок"
    ASH = "Пепел"
    SQUALL = "Вихрь"
    TORNADO = "Торнадо"
    CLEAR = "Ясно"
    CLOUDS = "Облачно"


class Weather(NamedTuple):
    """Data structure of weather."""

    temperature: Celsius
    weather_type: WeatherType
    weather_description: str
    wind_speed: Meters_per_second
    sunrise: datetime
    sunset: datetime
    city: str


def get_weather(coordinates: Coordinates) -> Weather:
    """Request weather in weather API service and return it."""
    if not config.OPEN_WEATHER_API_KEY:
        raise NoOpenWeatherApiKey(
            "There is no OPEN_WEATHER_API_KEY in your environment."
        )
    else:
        weather = _get_weather_by_command(
            shell_command.ShellCommand(
                executable=COMMAND_EXECUTABLE,
                arguments=[
                    config.OPEN_WEATHER_API_URL_PATTERN.format(
                        latitude=coordinates.latitude,
                        longitude=coordinates.longitude,
                        api_key=config.OPEN_WEATHER_API_KEY,
                        language=config.OPEN_WEATHER_API_LANG.value,
                    )
                ],
                no_internet_exit_code=COMMAND_NO_INTERNET_EXIT_CODE,
            )
        )
    return weather


def _get_weather_by_command(command: shell_command.ShellCommand) -> Weather:
    """Return weather by shell command."""
    try:
        command_output, *_ = command.execute()
    except CommandExecutionFailed as err:
        raise CantGetWeather(
            f"Can't get weather using {[command.executable, *command.arguments]} "
            f"command.\n{err}"
        )
    except UnicodeDecodeError as err:
        raise CantGetWeather(f"Can't decode shell command output:\n{err}")
    weather = _parse_weather(command_output)
    return weather


def _parse_weather(command_output: str) -> Weather:
    """Return weather from output of shell command."""
    # Regex pattern for dictionary with weather data
    weather_dictionary_pattern = r"{.*}"
    try:
        openweather_dict = json.loads(
            re.search(
                weather_dictionary_pattern, command_output
            ).group()  # type: ignore
        )
    except AttributeError:
        raise CantGetWeather(
            f"Shell command output:\n'{command_output}'\nhas no dictionary inside"
        )
    except JSONDecodeError:
        raise CantGetWeather(
            f"Shell command output:\n'{command_output}'\nhas no dictionary inside"
        )
    return Weather(
        temperature=_parse_temperature(openweather_dict),
        weather_type=_parse_weather_type(openweather_dict),
        weather_description=_parse_weather_description(openweather_dict),
        wind_speed=_parse_wind_speed(openweather_dict),
        sunrise=_parse_sun_time(openweather_dict, "sunrise"),
        sunset=_parse_sun_time(openweather_dict, "sunset"),
        city=_parse_city(openweather_dict),
    )


def _parse_temperature(openweather_dict: OpenWeatherDict) -> Celsius:
    """Return temperature from openweather response."""
    try:
        return round(openweather_dict["main"]["temp"])
    except KeyError:
        raise ApiServiceError(
            f"There is no temperature in expected place of "
            f"openweather response dictionary:\n{openweather_dict}"
        )


def _parse_weather_type(openweather_dict: OpenWeatherDict) -> WeatherType:
    """Return weather type from openweather response."""
    try:
        weather_type_id = str(openweather_dict["weather"][0]["id"])
    except IndexError:
        raise ApiServiceError(
            f"There is no weather type identifier in expected place "
            f"of openweather response dictionary:\n{openweather_dict}"
        )
    except KeyError:
        raise ApiServiceError(
            f"There is no weather type identifier in expected place "
            f"of openweather response dictionary:\n{openweather_dict}"
        )
    weather_types = {
        "2": WeatherType.THUNDERSTORM,
        "3": WeatherType.DRIZZLE,
        "5": WeatherType.RAIN,
        "6": WeatherType.SNOW,
        "701": WeatherType.MIST,
        "711": WeatherType.SMOKE,
        "721": WeatherType.HAZE,
        "731": WeatherType.DUST,
        "741": WeatherType.FOG,
        "751": WeatherType.SAND,
        "761": WeatherType.DUST,
        "762": WeatherType.ASH,
        "771": WeatherType.SQUALL,
        "781": WeatherType.TORNADO,
        "800": WeatherType.CLEAR,
        "80": WeatherType.CLOUDS,
    }
    for _id, _weather_type in weather_types.items():
        if weather_type_id.startswith(_id):
            return _weather_type
    raise ApiServiceError(
        f"Unknown weather type identifier {weather_type_id} "
        f"in openweather response dictionary:\n{openweather_dict}"
    )


def _parse_weather_description(openweather_dict: OpenWeatherDict) -> str:
    """Return weather description from openweather response."""
    try:
        return str(openweather_dict["weather"][0]["description"])
    except (IndexError, KeyError):
        raise ApiServiceError(
            f"There is no weather description in expected place of "
            f"openweather response dictionary:\n{openweather_dict}"
        )


def _parse_wind_speed(openweather_dict: OpenWeatherDict) -> Meters_per_second:
    """Return wind speed from openweather response."""
    try:
        return openweather_dict["wind"]["speed"]
    except KeyError:
        raise ApiServiceError(
            f"There is no wind speed in expected place of "
            f"openweather response dictionary:\n{openweather_dict}"
        )


def _parse_sun_time(
    openweather_dict: OpenWeatherDict, event: Literal["sunrise", "sunset"]
) -> datetime:
    """Return time of sunset or sunrise openweather response."""
    try:
        return datetime.fromtimestamp(openweather_dict["sys"][event])
    except KeyError:
        raise ApiServiceError(
            f"There is no sunrise or sunset time in expected place of "
            f"openweather response dictionary:\n{openweather_dict}"
        )


def _parse_city(openweather_dict: OpenWeatherDict) -> str:
    """Return city name openweather response."""
    try:
        return openweather_dict["name"]
    except KeyError:
        raise ApiServiceError(
            f"There is no city name in expected place of "
            f"openweather response dictionary:\n{openweather_dict}"
        )


if __name__ == "__main__":
    print(get_weather(Coordinates(latitude=55.50, longitude=49.20)))
