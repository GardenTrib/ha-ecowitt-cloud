"""Constants for Ecowitt Cloud integration."""

DOMAIN = "ecowitt_cloud"

# API
API_BASE_URL = "https://api.ecowitt.net/api/v3"
API_DEVICE_LIST = f"{API_BASE_URL}/device/list"
API_DEVICE_REAL_TIME = f"{API_BASE_URL}/device/real_time"
API_TIMEOUT = 30

# Config entry keys
CONF_APPLICATION_KEY = "application_key"
CONF_API_KEY = "api_key"
CONF_MAC = "mac"
CONF_GATEWAY_NAME = "gateway_name"
CONF_POLL_INTERVAL = "poll_interval"

# Defaults
DEFAULT_POLL_INTERVAL = 5  # minutes

# API rate limiting: 1500 req/day max
# At 5 min interval = 288 req/day — safe
API_MAX_DAILY_REQUESTS = 1500

# Sensor descriptions: (callback_key, field_key) -> metadata
SENSOR_DESCRIPTIONS: dict = {
    # Outdoor
    ("outdoor", "temperature"): {
        "name": "Outdoor Temperature",
        "device_class": "temperature",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
    },
    ("outdoor", "humidity"): {
        "name": "Outdoor Humidity",
        "device_class": "humidity",
        "state_class": "measurement",
        "icon": "mdi:water-percent",
    },
    # Indoor
    ("indoor", "temperature"): {
        "name": "Indoor Temperature",
        "device_class": "temperature",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
    },
    ("indoor", "humidity"): {
        "name": "Indoor Humidity",
        "device_class": "humidity",
        "state_class": "measurement",
        "icon": "mdi:water-percent",
    },
    # Solar & UV
    ("solar_and_uvi", "solar"): {
        "name": "Solar Radiation",
        "device_class": "irradiance",
        "state_class": "measurement",
        "icon": "mdi:weather-sunny",
    },
    ("solar_and_uvi", "uvi"): {
        "name": "UV Index",
        "device_class": None,
        "state_class": "measurement",
        "icon": "mdi:sun-wireless",
    },
    # Wind
    ("wind", "wind_speed"): {
        "name": "Wind Speed",
        "device_class": "wind_speed",
        "state_class": "measurement",
        "icon": "mdi:weather-windy",
    },
    ("wind", "wind_gust"): {
        "name": "Wind Gust",
        "device_class": "wind_speed",
        "state_class": "measurement",
        "icon": "mdi:weather-windy-variant",
    },
    ("wind", "wind_direction"): {
        "name": "Wind Direction",
        "device_class": None,
        "state_class": "measurement",
        "icon": "mdi:compass",
    },
    # Pressure
    ("pressure", "relative"): {
        "name": "Pressure",
        "device_class": "pressure",
        "state_class": "measurement",
        "icon": "mdi:gauge",
    },
    # Rainfall
    ("rainfall", "rain_rate"): {
        "name": "Rain Rate",
        "device_class": "precipitation_intensity",
        "state_class": "measurement",
        "icon": "mdi:weather-rainy",
    },
    ("rainfall", "daily"): {
        "name": "Daily Rain",
        "device_class": "precipitation",
        "state_class": "total_increasing",
        "icon": "mdi:weather-pouring",
    },
}

# Soil moisture channels (up to 16)
for _ch in range(1, 17):
    SENSOR_DESCRIPTIONS[(f"soil_ch{_ch}", "soilmoisture")] = {
        "name": f"Soil Moisture Ch{_ch}",
        "device_class": "moisture",
        "state_class": "measurement",
        "icon": "mdi:water-percent",
    }

# Soil sensor battery voltage channels (up to 16)
for _ch in range(1, 17):
    SENSOR_DESCRIPTIONS[("battery", f"soilmoisture_sensor_ch{_ch}")] = {
        "name": f"Soil Battery Ch{_ch}",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:battery",
    }

# Unit preferences
CONF_TEMP_UNIT = "temp_unit"
CONF_PRESSURE_UNIT = "pressure_unit"
CONF_WIND_UNIT = "wind_unit"
CONF_RAIN_UNIT = "rain_unit"

DEFAULT_TEMP_UNIT = "celsius"
DEFAULT_PRESSURE_UNIT = "hpa"
DEFAULT_WIND_UNIT = "kmh"
DEFAULT_RAIN_UNIT = "mm"

# Ecowitt API unit IDs
TEMP_UNIT_IDS = {"celsius": 1, "fahrenheit": 2}
PRESSURE_UNIT_IDS = {"hpa": 1, "inhg": 2}
WIND_UNIT_IDS = {"kmh": 2, "mph": 3}
RAIN_UNIT_IDS = {"mm": 1, "in": 2}

# WFC01 WittFlow fields (dynamic callback key = "WFC01-{serial}")
# Used in sensor.py and binary_sensor.py to create entities for any WFC01-* key found in data
WFC01_SENSOR_FIELDS: dict = {
    "flow_rate": {
        "name": "Flow Rate",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
        "icon": "mdi:water-pump",
    },
    "daily": {
        "name": "Daily Water",
        "device_class": "volume",
        "state_class": "total_increasing",
        "icon": "mdi:water",
    },
    "monthly": {
        "name": "Monthly Water",
        "device_class": "volume",
        "state_class": "total_increasing",
        "icon": "mdi:water",
    },
}

WFC01_BINARY_FIELDS: dict = {
    "status": {
        "name": "Valve",
        "device_class": "opening",
        "icon_on": "mdi:valve-open",
        "icon_off": "mdi:valve-closed",
    },
}

# Keep for binary_sensor.py import compatibility (now empty — WFC01 handled dynamically)
BINARY_SENSOR_DESCRIPTIONS: dict = {}
