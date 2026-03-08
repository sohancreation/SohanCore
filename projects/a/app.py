from flask import Flask, request, jsonify
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Retrieve API key from environment variables
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
if not WEATHER_API_KEY:
    logging.error("WEATHER_API_KEY environment variable not set.")
    WEATHER_API_KEY = "YOUR_API_KEY" # Provide a default value or handle the error gracefully


def get_weather_data(city):
    """Fetches weather data from OpenWeatherMap API."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"  # Use metric units for temperature
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        logging.info(f"Weather data fetched successfully for {city}.")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching weather data for {city}: {e}")
        return None


@app.route('/weather', methods=['GET'])
def weather():
    """API endpoint to get weather information for a city."""
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required.'}), 400

    weather_data = get_weather_data(city)

    if weather_data:
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']
        weather_info = {
            'city': city,
            'temperature': temperature,
            'humidity': humidity,
            'description': description
        }
        return jsonify(weather_info), 200
    else:
        return jsonify({'error': 'Failed to retrieve weather data.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
