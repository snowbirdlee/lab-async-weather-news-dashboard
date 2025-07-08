from aioconsole import ainput
import httpx
import asyncio
from dotenv import load_dotenv
import os

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
        print("Fetching weather and news...\n")
        weather, news = await asyncio.gather(
            get_weather(latitude, longitude),
            fetch_news(query=city)
        )
        
        if weather:
            print("\nWeather:")
            print(f"Temperature: {weather['temperature']}°C")
            print(f"Wind speed: {weather['windspeed']} m/s")    
        
        print("\n Top News:")
        for article in news:
            print(f"- {article['title']}")
            print(f"  {article['url']}")
        
    else:
        print("Cannot fetch weather without valid coordinates.")
        return
    
    
if __name__ == "__main__":
    asyncio.run(main())
