# Basic Weather Agent

A conversational AI weather assistant built with LangGraph and LangChain that provides comprehensive weather information for US cities using real-time data from the National Weather Service (NWS) API.

## Features

### Available Tools

- **Current Weather & Forecast**: Get detailed current conditions and 7-day forecast for any US city
- **Hourly Forecast**: 12-hour detailed forecast with temperature trends and precipitation chances
- **Weather Alerts**: Check for active weather alerts, watches, and warnings in your area
- **Solar & Lunar Information**: Sunrise/sunset times and current moon phase
- **Air Quality Index**: Real-time air quality data with health recommendations (requires API key)
- **Clothing Recommendations**: Smart suggestions for appropriate clothing and activities based on current weather

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/alfmat/basic-agent.git
   cd basic-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### Required Environment Variables

Create a `.env` file in the project root or set environment variables:

```bash
# Required: OpenAI API key for the language model
OPENAI_API_KEY=your_openai_api_key_here

# Optional: AirNow API key for air quality data
AIRNOW_API_KEY=your_airnow_api_key_here

# Optional: TimeZoneDB API key for accurate timezone information
TIMEZONE_API_KEY=your_timezone_api_key_here
```

### API Keys Setup

1. **OpenAI API Key** (Required):
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Generate an API key in your dashboard
   - Add to environment: `OPENAI_API_KEY=sk-...`

2. **AirNow API Key** (Optional - for air quality):
   - Register for free at [AirNow API](https://docs.airnowapi.org/account/request/)
   - Get your API key from the dashboard
   - Add to environment: `AIRNOW_API_KEY=...`

3. **TimeZoneDB API Key** (Optional - for solar/lunar data):
   - Sign up at [TimeZoneDB](https://timezonedb.com/)
   - Get your API key
   - Add to environment: `TIMEZONE_API_KEY=...`

## Usage

### Running the Agent

Start the interactive weather assistant:

```bash
python agent.py
```

### Commands

- **Weather Queries**: Ask about weather in any US city
  - "What's the weather like in New York?"
  - "Give me the forecast for Seattle"
  - "Is it raining in Chicago?"

- **Special Commands**:
  - `help` or `h`: Show available commands
  - `history`: View conversation history
  - `clear`: Clear conversation history
  - `quit`, `exit`, or `q`: Exit the program

### Example Interactions

```
💬 Ask about the weather (or 'quit' to exit): What's the weather in Boston?

🤖 Agent: Weather for Boston, Suffolk County, Massachusetts, United States:

📅 This Afternoon: Sunny, with a high near 75. West wind around 10 mph.

🌡️ Temperature: 75°F
💨 Wind: 10 mph W

📅 Tonight: Mostly clear, with a low around 55. West wind 5 to 10 mph.

🌡️ Temperature: 55°F
```

## Architecture

- **Framework**: LangGraph for agent orchestration, LangChain for LLM integration
- **Model**: OpenAI GPT-4.1-mini for conversational responses
- **Data Sources**:
  - National Weather Service (NWS) API for weather data
  - AirNow API for air quality
  - OpenStreetMap Nominatim for geocoding
  - Astral library for solar calculations
  - PyEphem for lunar phase calculations
- **Memory**: Conversation history maintained across sessions

## Limitations

- Currently limited to US cities (NWS API coverage)
- Air quality data requires API key
- Real-time data dependent on external API availability
- Solar/lunar data most accurate with TimeZoneDB API key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.