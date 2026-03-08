// app.js

const apiKey = 'YOUR_OPENWEATHERMAP_API_KEY'; // Replace with your actual API key
const defaultCity = 'London';

function getWeather(city) {
    fetch(`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`)
        .then(response => response.json())
        .then(data => {
            displayWeather(data);
        })
        .catch(error => {
            console.error('Error fetching weather:', error);
            document.getElementById('weather-data').innerText = 'Error fetching weather data.';
        });
}

function displayWeather(data) {
    const weatherData = document.getElementById('weather-data');
    if (data.cod === '404') {
        weatherData.innerText = 'City not found.';
        return;
    }
    const temperature = data.main.temp;
    const description = data.weather[0].description;
    const cityName = data.name;

    weatherData.innerHTML = `<h2>Weather in ${cityName}</h2><p>Temperature: ${temperature}°C</p><p>Description: ${description}</p>`;
}

document.addEventListener('DOMContentLoaded', () => {
    getWeather(defaultCity);

    document.getElementById('getWeather').addEventListener('click', () => {
        const city = document.getElementById('cityInput').value;
        getWeather(city);
    });
});