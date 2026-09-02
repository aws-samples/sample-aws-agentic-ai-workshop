from strands import Agent, tool
from strands_tools import calculator
import random

@tool
def weather_forecast(city: str, days: int = 3) -> str:
    """Gets the weather for a city.
        Args:
            city: Name of the city
            days: Forecast period (in days)
    """
    weather_options = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy", "Foggy"]
    selected_weather = random.choice(weather_options)

    print(f"Checking weather for {city} (forecast period: {days} days)...\n")
    print(f"Expected weather: {selected_weather}\n")
    print("="*10)
    return selected_weather

agent = Agent(
    tools=[weather_forecast, calculator]
    )

if __name__ == "__main__":
    user_input = "How's the weather in Seoul tomorrow?"

    response = agent(user_input) 
