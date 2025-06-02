import os
import requests
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CITY = "Seoul"
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 영어 → 한글 날씨 변환
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

        # 날씨 정보
        main_weather = data["weather"][0]["main"]
        icon = data["weather"][0]["icon"]

        # 현재 기온 및 습도
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        return {
            "weather": WEATHER_MAP.get(main_weather, "기타"),
            "temperature": temp,
            "humidity": humidity,
            "icon": icon
        }
    except Exception as e:
        return {"error": str(e)}
