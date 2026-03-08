// js/app.js

const apiKey = 'YOUR_API_KEY'; // Replace with your actual OpenWeatherMap API key
const cityInput = document.getElementById('city-input');
const searchBtn = document.getElementById('search-btn');
const weatherInfo = document.getElementById('weather-info');

searchBtn.addEventListener('click', () => {
    const city = cityInput.value;
    if (city) {
        getWeatherData(city);
    }
});

async function getWeatherData(city) {
    try {
        const apiUrl = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;
        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error('City not found');
        }

        const data = await response.json();
        displayWeatherData(data);
    } catch (error) {
        displayError(error.message);
    }
}

function displayWeatherData(data) {
    const { name, main, weather } = data;
    const temperature = main.temp;
    const description = weather[0].description;
    const icon = weather[0].icon;
    const iconUrl = `http://openweathermap.org/img/w/${icon}.png`;

    weatherInfo.innerHTML = `
        <h2>${name}</h2>
        <img src="${iconUrl}" alt="Weather Icon">
        <p>Temperature: ${temperature}°C</p>
        <p>Description: ${description}</p>
    `;
}

function displayError(message) {
    weatherInfo.innerHTML = `<p class="error">${message}</p>`;
}
