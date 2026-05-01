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

# Soil channels (up to 16)
SOIL_CHANNELS = [f"soil_ch{i}" for i in range(1, 17)]

# Water channels (up to 8)
WATER_CHANNELS = [f"water_ch{i}" for i in range(1, 9)]

# All callbacks for real_time API
ALL_CALLBACKS = [
    "outdoor",
    "indoor",
    "solar_and_uvi",
    "rainfall",
    "wind",
    "pressure",
] + SOIL_CHANNELS + WATER_CHANNELS

# Sensor keys mapping: (callback, field) -> sensor metadata
SENSOR_DESCRIPTIONS = {
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

# Dynamic sensor descriptions for soil channels
for _ch in range(1, 17):
    SENSOR_DESCRIPTIONS[(f"soil_ch{_ch}", "soilmoisture")] = {
        "name": f"Soil Moisture Ch{_ch}",
        "device_class": "moisture",
        "state_class": "measurement",
        "icon": "mdi:water-percent",
    }

# Dynamic sensor descriptions for water channels
for _ch in range(1, 9):
    SENSOR_DESCRIPTIONS[(f"water_ch{_ch}", "flow_velocity")] = {
        "name": f"Water Flow Ch{_ch}",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
        "icon": "mdi:water-pump",
    }
    SENSOR_DESCRIPTIONS[(f"water_ch{_ch}", "water_total")] = {
        "name": f"Water Total Ch{_ch}",
        "device_class": "volume",
        "state_class": "total_increasing",
        "icon": "mdi:water",
    }

# Binary sensor descriptions for water channels
BINARY_SENSOR_DESCRIPTIONS = {}
for _ch in range(1, 9):
    BINARY_SENSOR_DESCRIPTIONS[(f"water_ch{_ch}", "water_running")] = {
        "name": f"Valve Ch{_ch}",
        "device_class": "opening",
        "icon_on": "mdi:valve-open",
        "icon_off": "mdi:valve-closed",
    }
