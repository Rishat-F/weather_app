"""Preparing weather for printing in stdout."""

from weather_api_service import Weather


def format_weather(weather: Weather) -> str:
    """Format weather data in string."""
    return (
        f"{weather.city}, температура {weather.temperature}°C, "
        f"{weather.weather_type.value}\n"
        f"{weather.weather_description}\n"
        f"Ветер: {weather.wind_speed}\n"
        f"Восход: {weather.sunrise.strftime('%H:%M')}\n"
        f"Закат: {weather.sunset.strftime('%H:%M')}\n"
    )


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
