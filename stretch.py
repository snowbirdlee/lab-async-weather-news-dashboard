from aioconsole import ainput
import httpx
import asyncio
from dotenv import load_dotenv
import os
from rich import print

weather_descriptions = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

load_dotenv()
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
if not GNEWS_API_KEY:
    print("Error: GNEWS_API_KEY not found in .env file.")
    exit()

async def get_coords(city: str):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()
    
    if "results" in data and len(data["results"]) > 0:
        result = data["results"][0]
        return result["latitude"], result["longitude"]
    else:
        print("City not found.")
        return None, None # if there's no lat or lon. ChatGPT

async def get_weather(latitude, longitude):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()
    return data["current_weather"]

async def fetch_news(query):
    url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max=10&country=us&token={GNEWS_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    data = response.json()
    if "articles" in data:
        return data["articles"][:3]
    else:
        print("No news articles found.")
        return []

async def main():
    city = await ainput("City: ")
    latitude, longitude = await get_coords(city)
    if latitude is not None and longitude is not None:
        print("Fetching weather and news...")
        weather, news = await asyncio.gather(
            get_weather(latitude, longitude),
            fetch_news(query=city)
        )
        
        if weather:
            print(f"[bold blue]\nWeather in {city.title()}:[/bold blue]")
            print(f"Temperature: {weather['temperature']}°C")
            print(f"Wind speed: {weather['windspeed']} m/s") 
            print(f"Wind direction: {weather['winddirection']}°")  
            weathercode = weather["weathercode"] # ChatGPT
            description = weather_descriptions.get(weathercode, "Unknown weather") # if unknown weather code, returns "Unknown weather"
            print(f"Condition: {description}") 
        
        print(f"[bold purple]\nTop News in {city.title()}:[/bold purple]")
        for article in news:
            print(f"- {article['title']}")
            print(f"  {article['url']}")
        
    else:
        print("Cannot fetch weather without valid coordinates.")
        return
    
    
if __name__ == "__main__":
    asyncio.run(main())
