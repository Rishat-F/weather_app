"""Preparing weather for printing in stdout."""

import warnings
from enum import Enum
from typing import Any, Type, Union

import config
from config import SpeedUnit, TemperatureUnit
from converters import (
    convert_to_fahrenheit,
    convert_to_kelvin,
    convert_to_kph,
    convert_to_mph,
)
from patterns import measurement_unit_warning_pattern, weather_displaying_pattern
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
    return weather_displaying_pattern.format(
        city=weather.city.capitalize(),
        temperature=_convert_temperature(weather.temperature),
        temperature_unit=config.temperature_unit.value,
        weather_type=weather.weather_type.value,
        weather_description=weather.weather_description,
        wind_speed=_convert_speed(weather.wind_speed),
        speed_unit=config.speed_unit.value,
        sunrise=weather.sunrise.strftime("%H:%M"),
        sunset=weather.sunset.strftime("%H:%M"),
    )


def _convert_temperature(temperature: Celsius) -> Union[Kelvin, Fahrenheit, Celsius]:
    """Convert temperature."""
    default_unit = TemperatureUnit.CELSIUS
    if not _check_temperature_unit_type(config.temperature_unit, default_unit):
        config.temperature_unit = default_unit
    if config.temperature_unit is TemperatureUnit.KELVIN:
        return convert_to_kelvin(temperature)
    elif config.temperature_unit is TemperatureUnit.FAHRENHEIT:
        return convert_to_fahrenheit(temperature)
    else:
        return temperature


def _convert_speed(
    speed: Meters_per_second,
) -> Union[Miles_per_hour, Kilometers_per_hour, Meters_per_second]:
    """Convert speed."""
    default_unit = SpeedUnit.METERS_PER_SECOND
    if not _check_speed_unit_type(config.speed_unit, default_unit):
        config.speed_unit = default_unit
    if config.speed_unit is SpeedUnit.KILOMETERS_PER_HOUR:
        return convert_to_kph(speed)
    elif config.speed_unit is SpeedUnit.MILES_PER_HOUR:
        return convert_to_mph(speed)
    else:
        return speed


def _check_temperature_unit_type(unit: Any, default_unit: TemperatureUnit) -> bool:
    """
    Check if config temperature unit has right type.

    Warns if it wrong.
    """
    if not isinstance(unit, TemperatureUnit):
        _warn_wrong_measurement_unit(
            unit_var_name="config.temperature_unit",
            unit_value=unit,
            measurement="temperature",
            measurement_units_enum=TemperatureUnit,
            default_unit=default_unit,
        )
        return False
    return True


def _check_speed_unit_type(unit: Any, default_unit: SpeedUnit) -> bool:
    """
    Check if config speed unit has right type.

    Warns if it wrong.
    """
    if not isinstance(unit, SpeedUnit):
        _warn_wrong_measurement_unit(
            unit_var_name="config.speed_unit",
            unit_value=unit,
            measurement="speed",
            measurement_units_enum=SpeedUnit,
            default_unit=default_unit,
        )
        return False
    return True


def _warn_wrong_measurement_unit(
    unit_var_name: str,
    unit_value: Any,
    measurement: str,
    measurement_units_enum: Type[Enum],
    default_unit: Enum,
) -> None:
    """Warning if config measurement unit is wrong."""
    warnings.warn(
        measurement_unit_warning_pattern.format(
            unit_variable_name=unit_var_name,
            unit_variable_value=unit_value,
            measurement=measurement,
            available_measurement_units=", ".join(
                [str(unit) for unit in measurement_units_enum]
            ),
            titled_measurement=measurement.title(),
            default_unit=default_unit.value,
        )
    )
