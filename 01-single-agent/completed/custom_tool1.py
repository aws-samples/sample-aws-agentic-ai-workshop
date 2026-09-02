from strands import Agent, tool
from strands_tools import calculator
import random

@tool
def weather_forecast(city: str, days: int = 3) -> str:
    """도시의 날씨를 가져옵니다.
        Args:
            city: 도시의 이름
            days: 예측하려는 기간 (일 단위)
    """
    weather_options = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Foggy"]
    selected_weather = random.choice(weather_options)

    print(f"{city}의 날씨를 확인해보겠습니다 (검색 기간: {days}일)...\n")
    print(f"예상 날씨: {selected_weather}\n")
    print("="*10)
    return selected_weather

agent = Agent(
    tools=[weather_forecast, calculator]
    )

if __name__ == "__main__":
    user_input = "내일 서울 날씨 어때?"

    response = agent(user_input) 
