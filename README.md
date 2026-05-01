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

### Sensors
| Entity | Device Class | Unit |
|--------|-------------|------|
| Outdoor Temperature | temperature | from account |
| Outdoor Humidity | humidity | % |
| Indoor Temperature | temperature | from account |
| Indoor Humidity | humidity | % |
| Solar Radiation | irradiance | W/m² |
| UV Index | — | UV index |
| Wind Speed | wind_speed | from account |
| Wind Gust | wind_speed | from account |
| Wind Direction | — | ° |
| Pressure | pressure | from account |
| Rain Rate | precipitation_intensity | from account |
| Daily Rain | precipitation | from account |
| Soil Moisture Ch1–Ch16 | moisture | % |
| Water Flow Ch1–Ch8 | volume_flow_rate | from account |
| Water Total Ch1–Ch8 | volume | from account |

### Binary Sensors
| Entity | Device Class | Notes |
|--------|-------------|-------|
| Valve Ch1–Ch8 | opening | Open/closed state of WFC01 valves |

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
