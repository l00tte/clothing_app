
import requests

api_key = "d8010fa049994fddab9160209251602"


def generate_forecast():
    base_url = "http://api.weatherapi.com/v1/forecast.json?key=d8010fa049994fddab9160209251602&q=Berlin&days=5&aqi=no&alerts=no"

    response = requests.get(base_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()

        
        # Extract the min and max temperatures from the forecast data
        forecast_day = data["forecast"]["forecastday"][0]["day"]
        min_temp = forecast_day["mintemp_c"]
        max_temp = forecast_day["maxtemp_c"]
        current_temp = data["current"]["temp_c"]
        feels_like_temp = data["current"]["feelslike_c"]

        chance_of_rain = forecast_day["daily_will_it_rain"]

        forecast_tomorrow = data["forecast"]["forecastday"][1]["day"]
        
        max_temp_tomorrow = forecast_tomorrow["maxtemp_c"]
        print("tomorrow", max_temp_tomorrow)
        min_temp_tomorrow = forecast_tomorrow["mintemp_c"]
        chance_of_rain_tomorrow = forecast_tomorrow["daily_chance_of_rain"]

        forecast_days = data.get("forecast", {}).get("forecastday", [])

        forecast_next_5_days = {}

        for i in range(1, min(6, len(forecast_days))):  # Start from index 1 to skip today
            forecast_day = forecast_days[i]["day"]
            date = forecast_days[i]["date"]
            
            forecast_next_5_days[date] = {
                "max_temp": forecast_day["maxtemp_c"],
                "min_temp": forecast_day["mintemp_c"],
                "chance_of_rain": forecast_day["daily_chance_of_rain"],
            }

            return{
            "current_temp": current_temp,
            "feels_like_temp": feels_like_temp,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "chance_of_rain": chance_of_rain,
            "max_temp_tomorrow": max_temp_tomorrow,
            "min_temp_tomorrow": min_temp_tomorrow,
            "chance_of_rain_tomorrow": chance_of_rain_tomorrow,
            "forecast_next_5_days": forecast_next_5_days
        }

    
        
    else:
        print(f"Error: Unable to fetch data. Status code {response.status_code}")
        return print("Nope")


def generate_forecast_data():
    base_url = "http://api.weatherapi.com/v1/forecast.json?key=d8010fa049994fddab9160209251602&q=Berlin&days=5&aqi=no&alerts=no"

    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()

        return data
    
    else: 
        return None
