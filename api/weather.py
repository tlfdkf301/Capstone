import os
import requests
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CITY = "Seoul"
API_KEY = os.getenv("OPENWEATHER_API_KEY")
# 영어 날씨 → 한글 간단 변환
WEATHER_MAP = {
    "Clear": "맑음",
    "Clouds": "흐림",
    "Rain": "비",
    "Drizzle": "비",
    "Thunderstorm": "천둥",
    "Snow": "눈",
    "Mist": "안개",
    "Haze": "안개",
    "Smoke": "안개"
}

@router.get("/weather")
def get_weather():
    url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"q={CITY}&appid={API_KEY}&lang=kr&units=metric"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        main_weather = data["weather"][0]["main"]
        description = data["weather"][0]["description"]
        icon = data["weather"][0]["icon"]

        return {
            "weather": WEATHER_MAP.get(main_weather, "기타"),
            "description": description,
            "icon": icon
        }
    except Exception as e:
        return {"error": str(e)}