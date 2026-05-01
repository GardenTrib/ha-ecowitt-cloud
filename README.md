# Ecowitt Cloud — Home Assistant Integration

[![HACS Badge](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/release/GardenTrib/ha-ecowitt-cloud.svg)](https://github.com/GardenTrib/ha-ecowitt-cloud/releases)
[![License](https://img.shields.io/github/license/GardenTrib/ha-ecowitt-cloud.svg)](LICENSE)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

Home Assistant custom integration for the **Ecowitt Cloud API v3**. Connects your Ecowitt weather stations, soil sensors, and irrigation valves to Home Assistant via cloud polling.

---

## Features

- **Cloud polling** via [Ecowitt API v3](https://doc.ecowitt.net/web/#/apiv3en) — 5 to 60 min interval (288 req/day at 5 min, well within the 1500/day limit)
- **Multi-gateway** — add multiple gateways in a single setup, one device per gateway in HA
- **Dynamic units** — uses the units configured in your Ecowitt account, no manual conversion
- **Dynamic channels** — only creates entities for sensors actually present in the API response
- **Soil moisture** — up to 16 channels (WH51, WH51L)
- **Irrigation valves** — flow rate, total volume, open/closed status — up to 8 channels (WFC01 WittFlow)
- **Retry with backoff** — automatic retry on transient network errors (3 attempts, 5s/10s delays)

---

## Supported Hardware

| Device | Role |
|--------|------|
| GW3000 (and GW series) | Gateway |
| WH51 / WH51L | Soil moisture sensor (up to 16) |
| WFC01 WittFlow ½" | Irrigation valve (up to 8) |
| WH65, WH80, WH90 and compatible | Outdoor weather sensors |

---

## Entities

> Units are read dynamically from your Ecowitt account settings (metric or imperial).

### Weather sensors

| Entity | Unit (metric) | Unit (imperial) |
|--------|--------------|-----------------|
| Outdoor Temperature | °C | °F |
| Outdoor Humidity | % | % |
| Indoor Temperature | °C | °F |
| Indoor Humidity | % | % |
| Solar Radiation | W/m² | W/m² |
| UV Index | UV index | UV index |
| Wind Speed | km/h | mph |
| Wind Gust | km/h | mph |
| Wind Direction | ° | ° |
| Pressure | hPa | inHg |
| Rain Rate | mm/h | in/h |
| Daily Rain | mm | in |

### Soil sensors (WH51 / WH51L — up to 16 channels)

| Entity | Unit |
|--------|------|
| Soil Moisture Ch1 … Ch16 | % |

### Irrigation sensors (WFC01 WittFlow — up to 8 channels)

| Entity | Unit (metric) | Unit (imperial) |
|--------|--------------|-----------------|
| Water Flow Ch1 … Ch8 | L/min | gal/min |
| Water Total Ch1 … Ch8 | L | gal |

### Binary sensors

| Entity | State |
|--------|-------|
| Valve Ch1 … Ch8 | On = open / Off = closed |

---

## Installation

### Via HACS (recommended)

1. In Home Assistant, open **HACS → Integrations**
2. Search for **Ecowitt Cloud** and install
3. Restart Home Assistant

> If HACS doesn't find it yet, add it as a custom repository:
> HACS → ⋮ → Custom repositories → `https://github.com/GardenTrib/ha-ecowitt-cloud` → Integration

### Manual

1. Copy `custom_components/ecowitt_cloud/` to your HA `config/custom_components/` folder
2. Restart Home Assistant

---

## Configuration

### Prerequisites

Get your API keys at [api.ecowitt.net](https://api.ecowitt.net):
- **Application Key** — fixed key for your developer application
- **API Key** — your personal user key

### Setup

1. Go to **Settings → Integrations → + Add Integration**
2. Search for **Ecowitt Cloud**
3. Enter your **Application Key** and **API Key**
4. Select one or more gateways from the detected list
5. Set your preferred polling interval (5–60 min)

Each gateway appears as a separate device in Home Assistant, grouping all its sensors.

---

## License

MIT — see [LICENSE](LICENSE)
