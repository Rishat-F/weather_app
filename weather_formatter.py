"""Preparing weather for printing in stdout."""

import config
from config import WEATHER_DISPLAYING_PATTERN, SpeedUnit, TemperatureUnit
from converters import (
    convert_to_fahrenheit,
    convert_to_kelvin,
    convert_to_kph,
    convert_to_mph,
)
from weather_api_service import (
    Celsius,
    Fahrenheit,
    Kelvin,
    Kilometers_per_hour,
    Meters_per_second,
    Miles_per_hour,
    Weather,
)


def format_weather(weather: Weather) -> str:
    """Format weather data in string."""
    return WEATHER_DISPLAYING_PATTERN.format(
        city=weather.city.capitalize(),
        temperature=_convert_temperature(weather.temperature),
        temperature_unit=config.TEMPERATURE_UNIT.value,
        weather_type=weather.weather_type.value,
        weather_description=weather.weather_description,
        wind_speed=_convert_speed(weather.wind_speed),
        speed_unit=config.SPEED_UNIT.value,
        sunrise=weather.sunrise.strftime("%H:%M"),
        sunset=weather.sunset.strftime("%H:%M"),
    )


def _convert_temperature(temperature: Celsius) -> Kelvin | Fahrenheit | Celsius:
    """Convert temperature."""
    match config.TEMPERATURE_UNIT:
        case TemperatureUnit.KELVIN:
            return convert_to_kelvin(temperature)
        case TemperatureUnit.FAHRENHEIT:
            return convert_to_fahrenheit(temperature)
        case TemperatureUnit.CELSIUS:
            return temperature


def _convert_speed(
    speed: Meters_per_second,
) -> Miles_per_hour | Kilometers_per_hour | Meters_per_second:
    """Convert speed."""
    match config.SPEED_UNIT:
        case SpeedUnit.KILOMETERS_PER_HOUR:
            return convert_to_kph(speed)
        case SpeedUnit.MILES_PER_HOUR:
            return convert_to_mph(speed)
        case SpeedUnit.METERS_PER_SECOND:
            return speed


if __name__ == "__main__":
    from datetime import datetime

    from weather_api_service import WeatherType

    print(
        format_weather(
            Weather(
                temperature=20,
                weather_type=WeatherType.CLEAR,
                weather_description="Малооблачная погода",
                wind_speed=2.5,
                sunrise=datetime.fromisoformat("2022-05-03 04:00:00"),
                sunset=datetime.fromisoformat("2022-05-03 20:25:14"),
                city="Moscow",
            )
        )
    )
