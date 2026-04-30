# ha-ecowitt-cloud

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/hamzaharouchi/ha-ecowitt-cloud.svg)](https://github.com/hamzaharouchi/ha-ecowitt-cloud/releases)
[![License](https://img.shields.io/github/license/hamzaharouchi/ha-ecowitt-cloud.svg)](LICENSE)

**Home Assistant integration for Ecowitt weather stations via Cloud API and/or Local push.**

Supports all Ecowitt gateways (GW1000, GW1100, GW2000, GW3000 and compatible), weather sensors, up to 16 soil moisture channels, and up to 8 WFC01 water valve channels.

---

## Features

- ☁️ **Cloud mode** — polls the [Ecowitt Cloud API v3](https://doc.ecowitt.net/web/#/apiv3en)
- 🏠 **Local mode** — receives real-time push data directly from your gateway (no cloud needed)
- 🔄 **Auto mode** — Local priority with automatic Cloud fallback
- 📡 **Multi-gateway** — add multiple gateways in a single setup flow
- 🌱 **Dynamic soil channels** — up to 16 soil moisture sensors (only creates entities for detected channels)
- 💧 **WFC01 valve support** — flow rate, total volume, open/closed status (up to 8 channels)
- ⚙️ **Options flow** — change mode, port, and polling interval without reinstalling

---

## Supported Entities

### Sensors
| Entity | Device Class | Unit |
|--------|-------------|------|
| Outdoor Temperature | temperature | °C |
| Outdoor Humidity | humidity | % |
| Indoor Temperature | temperature | °C |
| Indoor Humidity | humidity | % |
| Solar Radiation | irradiance | W/m² |
| UV Index | — | UV index |
| Wind Speed | wind_speed | km/h |
| Wind Gust | wind_speed | km/h |
| Wind Direction | — | ° |
| Pressure | pressure | hPa |
| Rain Rate | precipitation_intensity | mm/h |
| Daily Rain | precipitation | mm |
| Soil Moisture Ch1–Ch16 | moisture | % |
| Water Flow Ch1–Ch8 | volume_flow_rate | L/min |
| Water Total Ch1–Ch8 | volume | L |

### Binary Sensors
| Entity | Device Class |
|--------|-------------|
| Valve Open/Closed Ch1–Ch8 | opening |

---

## Installation

### Via HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add: `https://github.com/hamzaharouchi/ha-ecowitt-cloud`
3. Category: **Integration**
4. Search for **Ecowitt Cloud** and install
5. Restart Home Assistant

### Manual

1. Copy `custom_components/ecowitt_cloud/` to your HA `config/custom_components/` folder
2. Restart Home Assistant

---

## Configuration

1. Go to **Settings → Integrations → + Add Integration**
2. Search for **Ecowitt Cloud**
3. Enter your **Application Key** and **API Key** from [api.ecowitt.net](https://api.ecowitt.net)
4. Select one or more gateways from the detected list
5. Choose your data mode:
   - **Cloud** — polling every 5–60 min (configurable), requires internet
   - **Local** — real-time push from gateway, configure your gateway to send data to HA
   - **Auto** — local first, cloud fallback if local unavailable

### Local mode gateway setup

In the **WS View Plus** app:
1. Menu → Device List → your gateway → Next → Next → **Customized**
2. Protocol: **Ecowitt**
3. Server IP: your Home Assistant IP
4. Path: `/`
5. Port: same as configured in the integration (default: `4199`)
6. Update interval: `60` seconds

---

## API Keys

Get your keys at [api.ecowitt.net](https://api.ecowitt.net):
- **Application Key** — fixed key for your application
- **API Key** — your personal user key

API rate limit: 1500 requests/day. At 5-min polling = ~288 req/day (well within limits).

---

## License

MIT License — see [LICENSE](LICENSE)
