import requests
from datetime import datetime
import pandas as pd

def get_weather(city: str) -> str:
    url = f"https://api.meteo.lt/v1/places/{city}/forecasts/long-term"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecast = data.get("forecastTimestamps", [])
        df = pd.DataFrame(forecast)
        df['forecastTimeUtc'] = pd.to_datetime(df['forecastTimeUtc'])
        # get data of tommorow
        tomorrow_date = (datetime.utcnow() + pd.Timedelta(days=1)).date()
        df = df[df['forecastTimeUtc'].dt.date == tomorrow_date]
    
        df = df[['forecastTimeUtc', 'airTemperature', 'feelsLikeTemperature', 'windSpeed', 'cloudCover', 'conditionCode']]
        df['forecastTimeUtc'] = df['forecastTimeUtc'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df.reset_index(drop=True, inplace=True)
        forecast = df.to_dict(orient='records')

        whole_text = ""
        for entry in forecast:
            # from dict create 'key - value' strings
            entry_str = ', '.join([f"{key} - {value}" for key, value in entry.items()])
            whole_text += entry_str + "\n"
        
        return whole_text
    else:
        return f"Error: Unable to fetch weather data for {city}."
    

if __name__ == "__main__":
    city = "vilnius"
    print(f"Fetching weather for {city}...")
    weather_info = get_weather(city)
    print(weather_info)