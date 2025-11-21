from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import requests
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
import ephem
import math
import pytz
import os
from langchain_openai import ChatOpenAI

def get_coordinates(city: str) -> Dict[str, float]:
    """Get latitude and longitude for a city using a geocoding service."""
    # Using OpenStreetMap Nominatim API (free, no API key required)
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        'q': city,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'us'  # Focus on US cities for NWS compatibility
    }
    headers = {
        'User-Agent': 'WeatherAgent/1.0'  # Required by Nominatim
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            return {
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon']),
                'display_name': data[0]['display_name']
            }
        else:
            raise ValueError(f"Could not find coordinates for {city}")
    except Exception as e:
        raise ValueError(f"Error getting coordinates for {city}: {str(e)}")

def get_nws_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """Get weather forecast from National Weather Service API."""
    try:
        # First, get the forecast office and grid coordinates
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {
            'User-Agent': 'WeatherAgent/1.0 (contact@example.com)'  # Required by NWS
        }
        
        points_response = requests.get(points_url, headers=headers)
        points_response.raise_for_status()
        points_data = points_response.json()
        
        # Get the forecast URL
        forecast_url = points_data['properties']['forecast']
        
        # Get the actual forecast
        forecast_response = requests.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        return forecast_data
    except Exception as e:
        raise ValueError(f"Error getting NWS forecast: {str(e)}")

def get_weather(city: str) -> str:
    """Get the current weather and forecast for a given city using NWS API."""
    try:
        # Get coordinates for the city
        coords = get_coordinates(city)
        lat, lon = coords['lat'], coords['lon']
        location_name = coords['display_name']
        
        # Get NWS forecast
        forecast_data = get_nws_forecast(lat, lon)
        
        # Extract relevant information
        periods = forecast_data['properties']['periods']
        current_period = periods[0]
        next_period = periods[1] if len(periods) > 1 else None
        
        # Format the response
        result = f"Weather for {location_name}:\n\n"
        result += f"📅 {current_period['name']}: {current_period['detailedForecast']}\n"
        result += f"🌡️ Temperature: {current_period['temperature']}°{current_period['temperatureUnit']}\n"
        result += f"💨 Wind: {current_period['windSpeed']} {current_period['windDirection']}\n"
        
        if next_period:
            result += f"\n📅 {next_period['name']}: {next_period['shortForecast']}\n"
            result += f"🌡️ Temperature: {next_period['temperature']}°{next_period['temperatureUnit']}\n"
        
        return result
        
    except ValueError as e:
        return f"Sorry, I couldn't get weather information: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def get_hourly_forecast(city: str) -> str:
    """Get hourly weather forecast with temperature and precipitation details for a given city."""
    try:
        # Get coordinates for the city
        coords = get_coordinates(city)
        lat, lon = coords['lat'], coords['lon']
        location_name = coords['display_name']
        
        # Get the forecast office and grid coordinates for hourly data
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        headers = {
            'User-Agent': 'WeatherAgent/1.0 (contact@example.com)'
        }
        
        points_response = requests.get(points_url, headers=headers)
        points_response.raise_for_status()
        points_data = points_response.json()
        
        # Get hourly forecast URL
        hourly_url = points_data['properties']['forecastHourly']
        
        # Get hourly forecast data
        hourly_response = requests.get(hourly_url, headers=headers)
        hourly_response.raise_for_status()
        hourly_data = hourly_response.json()
        
        periods = hourly_data['properties']['periods'][:12]  # Next 12 hours
        
        # Extract data for analysis
        temperatures = []
        precipitation_chances = []
        
        for period in periods:
            temperatures.append(period['temperature'])
            
            # Extract precipitation probability
            precip_prob = period.get('probabilityOfPrecipitation', {})
            if precip_prob and 'value' in precip_prob:
                precipitation_chances.append(precip_prob['value'] or 0)
            else:
                precipitation_chances.append(0)
        
        # Format text summary
        result = f"🕐 12-Hour Hourly Forecast for {location_name.split(',')[0]}:\n\n"
        
        # Show detailed hourly breakdown
        for i, period in enumerate(periods):
            start_time = datetime.fromisoformat(period['startTime'].replace('Z', '+00:00'))
            time_str = start_time.strftime('%I %p').lstrip('0')
            temp = period['temperature']
            precip = precipitation_chances[i]
            short_forecast = period.get('shortForecast', 'Clear')
            
            result += f"• {time_str}: {temp}°F - {short_forecast}"
            if precip > 0:
                result += f" ({precip}% rain chance)"
            result += "\n"
        
        # Summary statistics
        min_temp = min(temperatures)
        max_temp = max(temperatures)
        max_precip = max(precipitation_chances)
        
        result += f"\n📊 Summary:\n"
        result += f"  🌡️ Temperature Range: {min_temp}°F to {max_temp}°F\n"
        result += f"  ☔ Highest Rain Chance: {max_precip}%\n"
        
        return result
        
    except Exception as e:
        return f"Error getting hourly forecast: {str(e)}"

def get_weather_alerts(city: str) -> str:
    """Get active weather alerts, watches, and warnings for a given city."""
    try:
        # Get coordinates for the city
        coords = get_coordinates(city)
        lat, lon = coords['lat'], coords['lon']
        location_name = coords['display_name']
        
        # Get alerts for the area
        alerts_url = f"https://api.weather.gov/alerts/active"
        params = {
            'point': f"{lat},{lon}"
        }
        headers = {
            'User-Agent': 'WeatherAgent/1.0 (contact@example.com)'
        }
        
        response = requests.get(alerts_url, params=params, headers=headers)
        response.raise_for_status()
        alerts_data = response.json()
        
        features = alerts_data.get('features', [])
        
        if not features:
            return f"✅ No active weather alerts for {location_name.split(',')[0]}"
        
        result = f"🚨 Active Weather Alerts for {location_name}:\n\n"
        
        for feature in features:
            props = feature['properties']
            event = props.get('event', 'Unknown Event')
            severity = props.get('severity', 'Unknown')
            urgency = props.get('urgency', 'Unknown')
            description = props.get('description', 'No description available')
            
            # Emoji mapping for severity
            severity_emoji = {
                'Extreme': '🔴',
                'Severe': '🟠', 
                'Moderate': '🟡',
                'Minor': '🟢',
                'Unknown': '⚪'
            }
            
            emoji = severity_emoji.get(severity, '⚪')
            
            result += f"{emoji} **{event}** ({severity})\n"
            result += f"   📍 Urgency: {urgency}\n"
            
            # Truncate long descriptions
            if len(description) > 200:
                description = description[:200] + "..."
            result += f"   📝 {description}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error getting weather alerts: {str(e)}"

def get_solar_lunar_info(city: str) -> str:
    """Get sunrise, sunset, and moon phase information for a given city."""
    try:
        # Get coordinates for the city
        coords = get_coordinates(city)
        lat, lon = coords['lat'], coords['lon']
        location_name = coords['display_name']
        
        # Get timezone using coordinate-based API lookup
        coord_url = f"https://api.timezonedb.com/v2.1/get-time-zone"
        params = {
            'key': os.getenv("TIMEZONE_API_KEY"),  # Use demo key for testing, replace with real key
            'format': 'json',
            'by': 'position',
            'lat': lat,
            'lng': lon
        }
        
        try:
            tz_response = requests.get(coord_url, params=params, timeout=10)
            tz_response.raise_for_status()
            tz_data = tz_response.json()
            
            if tz_data.get('status') == 'OK':
                tz_name = tz_data.get('zoneName', 'UTC')
            else:
                # If API fails, raise an error instead of falling back
                raise ValueError(f"Timezone lookup failed: {tz_data.get('message', 'Unknown error')}")
                
        except Exception as e:
            return f"Error getting timezone information: {str(e)}. Please try again later."
        
        # Create location for astral calculations
        location = LocationInfo()
        location.latitude = lat
        location.longitude = lon
        location.timezone = tz_name
        
        # Get sun times for today
        today = datetime.now().date()
        s = sun(location.observer, date=today)
        
        # Convert to local timezone for display
        local_tz = pytz.timezone(tz_name)
        sunrise_local = s['sunrise'].astimezone(local_tz)
        sunset_local = s['sunset'].astimezone(local_tz)
        
        sunrise = sunrise_local.strftime('%I:%M %p').lstrip('0')
        sunset = sunset_local.strftime('%I:%M %p').lstrip('0')
        
        # Calculate moon phase using ephem
        moon = ephem.Moon()
        moon.compute(datetime.now())
        moon_phase = moon.moon_phase
        
        # Convert moon phase to description
        if moon_phase < 0.1:
            phase_desc = "🌑 New Moon"
        elif moon_phase < 0.3:
            phase_desc = "🌒 Waxing Crescent"
        elif moon_phase < 0.7:
            phase_desc = "🌓 First Quarter"
        elif moon_phase < 0.9:
            phase_desc = "🌔 Waxing Gibbous"
        elif moon_phase < 1.1:
            phase_desc = "🌕 Full Moon"
        elif moon_phase < 1.3:
            phase_desc = "🌖 Waning Gibbous"
        elif moon_phase < 1.7:
            phase_desc = "🌗 Last Quarter"
        else:
            phase_desc = "🌘 Waning Crescent"
        
        # Get timezone display name
        tz_display = tz_name.split('/')[-1].replace('_', ' ')
        
        result = f"🌅 Solar & Lunar Info for {location_name.split(',')[0]}:\n\n"
        result += f"🌅 Sunrise: {sunrise} ({tz_display} Time)\n"
        result += f"🌅 Sunset: {sunset} ({tz_display} Time)\n"
        result += f"🌙 Moon Phase: {phase_desc} ({moon_phase:.1%} illuminated)\n"
        
        # Calculate daylight hours
        daylight_duration = sunset_local - sunrise_local
        hours = int(daylight_duration.total_seconds() // 3600)
        minutes = int((daylight_duration.total_seconds() % 3600) // 60)
        result += f"☀️ Daylight: {hours}h {minutes}m\n"
        
        return result
        
    except Exception as e:
        return f"Error getting solar/lunar information: {str(e)}"

def get_air_quality(city: str) -> str:
    """Get air quality index and information for a given city."""
    try:
        # Get coordinates for the city
        coords = get_coordinates(city)
        lat, lon = coords['lat'], coords['lon']
        location_name = coords['display_name']
        
        # AirNow API implementation
        # Get API key from environment variable
        api_key = os.getenv('AIRNOW_API_KEY')
        
        if not api_key:
            # Return instructions for getting API key
            result = f"🌬️ Air Quality for {location_name.split(',')[0]}:\n\n"
            result += "⚠️ AirNow API key required for real-time air quality data.\n\n"
            result += "📝 To enable this feature:\n"
            result += "1. Register for free at: https://docs.airnowapi.org/account/request/\n"
            result += "2. Get your API key from the dashboard\n"
            result += "3. Set environment variable: AIRNOW_API_KEY=your_key_here\n"
            result += "4. Restart the application\n\n"
            result += "📊 Demo AQI: 42 (Good)\n"
            result += "🟢 Air quality is satisfactory for outdoor activities\n"
            result += "💡 PM2.5: 8.2 μg/m³, Ozone: 0.045 ppm"
            return result
        
        # Make API call to AirNow
        base_url = "http://www.airnowapi.org/aq/observation/latLong/current/"
        params = {
            'format': 'application/json',
            'latitude': lat,
            'longitude': lon,
            'distance': 25,  # Search within 25 miles
            'API_KEY': api_key
        }
        
        headers = {
            'User-Agent': 'WeatherAgent/1.0'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            return f"🌬️ No air quality data available for {location_name.split(',')[0]} within 25 miles."
        
        # Process the air quality data
        result = f"🌬️ Air Quality for {location_name.split(',')[0]}:\n\n"
        
        # Group data by parameter (PM2.5, PM10, Ozone)
        pollutants = {}
        for reading in data:
            param = reading.get('ParameterName', 'Unknown')
            aqi = reading.get('AQI', 0)
            category = reading.get('Category', {}).get('Name', 'Unknown')
            
            pollutants[param] = {
                'aqi': aqi,
                'category': category,
                'reporting_area': reading.get('ReportingArea', 'Unknown')
            }
        
        # Find the highest AQI to determine overall air quality
        max_aqi = 0
        overall_category = 'Good'
        for param, info in pollutants.items():
            if info['aqi'] > max_aqi:
                max_aqi = info['aqi']
                overall_category = info['category']
        
        # Category emoji mapping
        category_emoji = {
            'Good': '🟢',
            'Moderate': '🟡', 
            'Unhealthy for Sensitive Groups': '🟠',
            'Unhealthy': '🔴',
            'Very Unhealthy': '🟣',
            'Hazardous': '🟤'
        }
        
        emoji = category_emoji.get(overall_category, '⚪')
        
        result += f"📊 Overall AQI: {max_aqi} - {overall_category} {emoji}\n\n"
        
        # Detail each pollutant
        for param, info in pollutants.items():
            param_emoji = {
                'PM2.5': '🔬',
                'PM10': '💨', 
                'OZONE': '☁️',
                'O3': '☁️'
            }.get(param, '📈')
            
            result += f"{param_emoji} {param}: AQI {info['aqi']} ({info['category']})\n"
        
        # Health recommendations based on overall AQI
        result += f"\n💡 Health Guidance:\n"
        if max_aqi <= 50:  # Good
            result += "   ✅ Air quality is good. Ideal for outdoor activities.\n"
        elif max_aqi <= 100:  # Moderate
            result += "   ⚠️ Acceptable for most people. Sensitive individuals may experience minor issues.\n"
        elif max_aqi <= 150:  # Unhealthy for Sensitive Groups
            result += "   🟠 Sensitive groups should limit prolonged outdoor exertion.\n"
        elif max_aqi <= 200:  # Unhealthy
            result += "   � Everyone should limit prolonged outdoor exertion.\n"
        elif max_aqi <= 300:  # Very Unhealthy
            result += "   � Everyone should avoid prolonged outdoor exertion.\n"
        else:  # Hazardous
            result += "   🟤 Emergency conditions. Everyone should avoid outdoor activities.\n"
        
        # Add reporting area info
        if pollutants:
            first_pollutant = next(iter(pollutants.values()))
            result += f"\n📍 Data from: {first_pollutant['reporting_area']}"
        
        return result
        
    except requests.exceptions.RequestException as e:
        return f"🌬️ Error connecting to AirNow API: {str(e)}\nPlease check your internet connection and API key."
    except Exception as e:
        return f"Error getting air quality: {str(e)}"

def recommend_clothing(city: str) -> str:
    """Recommend clothing and activities based on current weather conditions."""
    try:
        # Get coordinates for the city
        coords = get_coordinates(city)
        lat, lon = coords['lat'], coords['lon']
        location_name = coords['display_name']
        
        # Get current weather forecast
        forecast_data = get_nws_forecast(lat, lon)
        current_period = forecast_data['properties']['periods'][0]
        
        temp = current_period['temperature']
        temp_unit = current_period['temperatureUnit']
        wind_speed = current_period['windSpeed']
        forecast = current_period['shortForecast'].lower()
        
        # Convert to Fahrenheit if needed
        if temp_unit == 'C':
            temp = (temp * 9/5) + 32
        
        result = f"👔 Clothing & Activity Recommendations for {location_name.split(',')[0]}:\n\n"
        result += f"🌡️ Current: {temp}°F, {current_period['shortForecast']}\n\n"
        
        # Temperature-based clothing recommendations
        if temp >= 80:
            clothing = "👕 Light, breathable clothing (t-shirt, shorts, sandals)"
            activities = "🏊 Great for: Swimming, outdoor sports, beach activities"
        elif temp >= 70:
            clothing = "👖 Comfortable casual wear (light pants, short sleeves)"
            activities = "🚶 Great for: Walking, hiking, outdoor dining"
        elif temp >= 60:
            clothing = "🧥 Light layers (long sleeves, light jacket optional)"
            activities = "🍂 Great for: Jogging, cycling, fall activities"
        elif temp >= 50:
            clothing = "🧥 Jacket or sweater recommended"
            activities = "🥾 Great for: Hiking with layers, outdoor photography"
        elif temp >= 40:
            clothing = "🧥 Warm coat, long pants, closed shoes"
            activities = "☕ Better for: Indoor activities, brief outdoor walks"
        elif temp >= 32:
            clothing = "🧥 Heavy coat, hat, gloves, warm layers"
            activities = "❄️ Bundle up for: Winter sports, holiday activities"
        else:
            clothing = "🧥 Full winter gear - coat, hat, gloves, insulated boots"
            activities = "🏠 Consider: Indoor activities, limit outdoor exposure"
        
        result += f"👔 {clothing}\n"
        result += f"🎯 {activities}\n\n"
        
        # Weather condition adjustments
        if 'rain' in forecast or 'shower' in forecast:
            result += "☔ Rain expected - bring umbrella or raincoat\n"
        if 'snow' in forecast:
            result += "❄️ Snow expected - wear waterproof boots and warm layers\n"
        if 'wind' in forecast or any(char.isdigit() for char in wind_speed):
            result += "💨 Windy conditions - consider windproof outer layer\n"
        if 'sun' in forecast or 'clear' in forecast:
            result += "☀️ Sunny conditions - don't forget sunscreen and sunglasses\n"
        
        return result
        
    except Exception as e:
        return f"Error getting clothing recommendations: {str(e)}"

model = ChatOpenAI(
    model="gpt-5.1",
    temperature=0
)

# Create a memory saver for conversation state
memory = MemorySaver()

agent = create_agent(
    tools=[
        get_weather,
        get_hourly_forecast,
        get_weather_alerts,
        get_solar_lunar_info,
        get_air_quality,
        recommend_clothing
    ],
    model=model,
    system_prompt="""You are a helpful AI weather assistant with comprehensive weather analysis capabilities. 

Available tools:
- get_weather: Get current weather and basic forecast for US cities
- get_hourly_forecast: Get detailed 24-hour forecast with temperature charts
- get_weather_alerts: Check for active weather alerts, watches, and warnings
- get_solar_lunar_info: Get sunrise, sunset, and moon phase information
- get_air_quality: Get air quality index and recommendations
- recommend_clothing: Suggest appropriate clothing and activities based on weather

You can provide real-time weather data from the National Weather Service, create visual forecasts, and give practical advice. You maintain conversation context and can refer to previous queries or locations discussed. Be conversational, helpful, and proactive in suggesting relevant information.""",
    checkpointer=memory
)

def main():
    """Main function to run the weather agent."""
    # Create a unique thread ID for this conversation session
    thread_id = "weather_conversation"
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        user_input = input("\n💬 Ask about the weather (or 'quit' to exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_input.lower() in ['help', 'h']:
            print("🆘 Available commands:")
            print("  - Ask about weather in any US city")
            print("  - 'history' - Show conversation history")
            print("  - 'clear' - Clear conversation history")
            print("  - 'help' or 'h' - Show this help")
            print("  - 'quit', 'exit', or 'q' - Exit the program")
            continue
            
        if user_input.lower() == 'history':
            print("📜 Conversation History:")
            try:
                # Get the current state from memory
                state = agent.get_state(config)
                if not state.values.get("messages"):
                    print("  No conversation history yet.")
                else:
                    for i, msg in enumerate(state.values["messages"], 1):
                        if hasattr(msg, 'content') and msg.content:
                            role = type(msg).__name__.replace('Message', '').lower()
                            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                            print(f"  {i}. {role}: {content}")
            except Exception as e:
                print(f"  Error retrieving history: {str(e)}")
            continue
            
        if user_input.lower() == 'clear':
            # Create a new thread ID to effectively clear history
            import uuid
            thread_id = f"weather_conversation_{uuid.uuid4().hex[:8]}"
            config = {"configurable": {"thread_id": thread_id}}
            print("🧹 Conversation history cleared!")
            continue
        
        if not user_input:
            continue
            
        try:
            # Invoke agent with the input and thread configuration
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
            
            # Extract and print the final AI response
            final_response = result["messages"][-1].content
            print(f"🤖 Agent: {final_response}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🌤️ Welcome to the Conversational Weather Agent!")
    print("Ask me about the weather in any US city. I'll remember our conversation!")
    print("Type 'help' for available commands.")
    main()