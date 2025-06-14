import requests
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import unquote, quote

def home(request):
    return render(request, 'weather_app/home.html')

# views.py

import json
from django.http import JsonResponse
from django.views import View


class CityAutocomplete(View):
    def get(self, request):
        term = request.GET.get('term')
        with open('cities.json', 'r') as f:
            cities = json.load(f)
            city_names = [city['name'] for city in cities if term.lower() in city['name'].lower()]

        return JsonResponse(city_names, safe=False)

def get_weather(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        api_key = '45b01a7f6a9893cc9370a6fd91f105fb'
        weather_url = f'http://api.openweathermap.org/data/2.5/forecast?q={location}&units=metric&appid={api_key}'
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            weather_data = response.json()
            if 'list' in weather_data:
                current_weather = {
                    'temperature': weather_data['list'][0]['main']['temp'],
                    'humidity': weather_data['list'][0]['main']['humidity'],
                    'pressure': weather_data['list'][0]['main']['pressure'],
                    'wind': weather_data['list'][0]['wind']['speed'],
                    'description': weather_data['list'][0]['weather'][0]['description']
                }
                hourly_forecast = weather_data['list'][:8]  # next 24 hours (3-hour intervals)
                weekly_forecast = weather_data['list'][::8]  # next 7 days (24-hour intervals)
                
                context = {
                    'current_weather': current_weather,
                    'hourly_forecast': hourly_forecast,
                    'weekly_forecast': weekly_forecast,
                    'location': location
                }
                
                return render(request, 'weather_app/weather.html', context)
            else:
                error_message = "Weather data not found for the specified location."
        else:
            error_message = f"Error fetching weather data: {response.status_code}"
        
        return render(request, 'weather_app/home.html', {'error_message': error_message})
    return render(request, 'weather_app/home.html')

def map_view(request):
    return render(request, 'weather_app/map.html')
    
import requests
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from urllib.parse import unquote, quote

def reverse_geocode(lat, lon):
    api_key = '45b01a7f6a9893cc9370a6fd91f105fb'
    geocode_url = f'http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}'
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['name']
    return None

def geocode(location_name):
    api_key = '45b01a7f6a9893cc9370a6fd91f105fb'
    geocode_url = f'http://api.openweathermap.org/geo/1.0/direct?q={location_name}&limit=1&appid={api_key}'
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None, None

def download_report(request, location):
    location = unquote(location)
    api_key = '45b01a7f6a9893cc9370a6fd91f105fb'

    lat, lon = None, None
    if ',' in location:
        lat, lon = location.split(',')
    else:
        lat, lon = geocode(location)
    
    if lat and lon:
        weather_url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}'
    else:
        location_encoded = quote(location)
        weather_url = f'http://api.openweathermap.org/data/2.5/forecast?q={location_encoded}&units=metric&appid={api_key}'

    print(f"Fetching weather data from: {weather_url}")  # Debug statement

    response = requests.get(weather_url)
    
    if response.status_code == 200:
        weather_data = response.json()

        if 'list' in weather_data:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={location}_weather_report.pdf'
            
            p = canvas.Canvas(response, pagesize=letter)
            width, height = letter
            
            p.drawString(100, height - 50, f"Weather Report for {location}")
            p.drawString(100, height - 80, f"Temperature: {weather_data['list'][0]['main']['temp']}°C")
            p.drawString(100, height - 110, f"Humidity: {weather_data['list'][0]['main']['humidity']}%")
            p.drawString(100, height - 140, f"Pressure: {weather_data['list'][0]['main']['pressure']} hPa")
            p.drawString(100, height - 170, f"Wind: {weather_data['list'][0]['wind']['speed']} m/s")
            p.drawString(100, height - 200, f"Description: {weather_data['list'][0]['weather'][0]['description']}")
            
            p.drawString(100, height - 240, "Hourly Forecast:")
            y = height - 270
            for forecast in weather_data['list'][:8]:
                p.drawString(100, y, f"{forecast['dt_txt']}: {forecast['main']['temp']}°C, {forecast['main']['humidity']}% humidity")
                y -= 20
            
            p.drawString(100, y - 20, "Weekly Forecast:")
            y -= 50
            for forecast in weather_data['list'][::8]:
                p.drawString(100, y, f"{forecast['dt_txt']}: {forecast['main']['temp']}°C, {forecast['main']['humidity']}% humidity")
                y -= 20
            
            p.showPage()
            p.save()
            
            return response
        else:
            print(f"No 'list' key in weather data for {location}")  # Debug statement
            return HttpResponse(f"Error: No weather data found for {location}.", content_type='text/plain')
    else:
        print(f"Error fetching weather data: {response.status_code}")  # Debug statement
        return HttpResponse(f"Error fetching weather data: {response.status_code}", content_type='text/plain')

def get_weather_by_coordinates(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        api_key = '45b01a7f6a9893cc9370a6fd91f105fb'
        weather_url = f'http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={api_key}'
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            weather_data = response.json()
            if 'list' in weather_data:
                location_name = reverse_geocode(latitude, longitude)
                current_weather = {
                    'temperature': weather_data['list'][0]['main']['temp'],
                    'humidity': weather_data['list'][0]['main']['humidity'],
                    'pressure': weather_data['list'][0]['main']['pressure'],
                    'wind': weather_data['list'][0]['wind']['speed'],
                    'description': weather_data['list'][0]['weather'][0]['description']
                }
                hourly_forecast = weather_data['list'][:8]  # next 24 hours (3-hour intervals)
                weekly_forecast = weather_data['list'][::8]  # next 7 days (24-hour intervals)
                
                context = {
                    'current_weather': current_weather,
                    'hourly_forecast': hourly_forecast,
                    'weekly_forecast': weekly_forecast,
                    'latitude': latitude,
                    'longitude': longitude,
                    'location': location_name or f"{latitude},{longitude}"
                }
                
                return render(request, 'weather_app/weather.html', context)
            else:
                error_message = "Weather data not found for the specified location."
        else:
            error_message = f"Error fetching weather data: {response.status_code}"
        
        return render(request, 'weather_app/map.html', {'error_message': error_message})
    return render(request, 'weather_app/map.html')