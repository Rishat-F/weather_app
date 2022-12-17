"""Patterns."""

open_weather_api_url_pattern = (
    "https://api.openweathermap.org/data/2.5/weather?"
    "lat={latitude}&"
    "lon={longitude}&"
    "appid={api_key}&"
    "lang={language}&"
    "units=metric"
)


weather_displaying_pattern = (
    "{city}, {temperature}{temperature_unit}, {weather_type}\n\n"
    "{weather_description}\n"
    "Ветер: {wind_speed}{speed_unit}\n"
    "Восход: {sunrise}\n"
    "Закат: {sunset}\n"
)


measurement_unit_warning_pattern = (
    "No such option for {unit_variable_name}: '{unit_variable_value}'. "
    "Available measurement units for {measurement} are "
    "{available_measurement_units}. {titled_measurement} shown in {default_unit}."
)


language_warning_patter = (
    "No such option for {language_variable_name}: '{language_variable_value}'. "
    "Available languages are {available_languages}."
)
