import os, json, requests, time
from reg_parserlib import extract_using_regex

def execute(question: str, parameter):
    print(f"File Name: {os.path.basename(__file__)[0]}")

    city, country = get_city_country_name(question)

    # Detect whether to get minimum or maximum latitude
    mode = "max" if "maximum" in question.lower() else "min"

    latitude = get_latitude_nominatim(city, country, mode)
    return latitude

def get_latitude_nominatim(city, country, mode="max"):
    """Fetch the min or max latitude of a city's bounding box using Nominatim API."""
    url = 'https://nominatim.openstreetmap.org/search'
    params = {'q': f'{city}, {country}', 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'UrbanRideApp/1.0 (contact@urbanride.com)'}

    for attempt in range(3):
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 403:
            print("❌ Access forbidden. Retrying in 10 seconds...")
            time.sleep(10)
            continue

        response.raise_for_status()
        data = response.json()

        if data:
            bounding_box = data[0]['boundingbox']  # [south_lat, north_lat, west_lon, east_lon]
            latitudes = list(map(float, bounding_box[:2]))  # Extract latitude range
            return max(latitudes) if mode == "max" else min(latitudes)

    print("⚠ Nominatim API blocked. Switching to OpenCage API...")
    return get_latitude_opencage(city, country, mode)

def get_latitude_opencage(city, country, mode="max"):
    """Fetch min or max latitude using OpenCage API."""
    API_KEY = 'YOUR_OPENCAGE_API_KEY'  # Replace with your actual API key
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {'q': f'{city}, {country}', 'key': API_KEY}

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    if not data['results']:
        raise ValueError(f"🚨 No data found for {city}, {country}")

    bounds = data['results'][0]['bounds']
    latitudes = [bounds['northeast']['lat'], bounds['southwest']['lat']]
    return max(latitudes) if mode == "max" else min(latitudes)

def get_city_country_name(text):
    regex_patterns = {
        "city": {"pattern": r'city ([\w\s]+) in the country ([\w\s]+) on the Nominatim API', "multiple": True}
    }
    reg_params = extract_using_regex(regex_patterns, text)
    city = reg_params["city"][-1][0] if "city" in reg_params else "Chennai"
    country = reg_params["city"][-1][1] if "city" in reg_params else "India"
    
    return city, country
