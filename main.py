import os
from dotenv import load_dotenv
import requests
import json
from maps import render_clean_map

def get_vehicle_locations(api_key, agency="SF"):
    """
    Fetch vehicle locations from 511 API.
    """
    url = "http://api.511.org/transit/VehicleMonitoring"
    params = {
        "api_key": api_key,
        "agency": agency,
        "format": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        remaining = response.headers.get('RateLimit-Remaining')
        total = response.headers.get('RateLimit-Limit')

        if remaining:
            try:
                remaining_count = int(remaining)
                total_count = int(total)
                print(f"API Rate Limit Remaining: {remaining_count}/{total_count}")
                if remaining_count < 10:
                    print("⚠️  WARNING: Rate limit is critically low (< 10)! Pausing or stopping recommended.")
            except ValueError:
                print(f"Could not parse RateLimit-Remaining header: {remaining}")
        

        # The API might return BOM, so decode with utf-8-sig
        content = response.content.decode('utf-8-sig')
        
        # Sometimes the API returns a leading character or whitespace
        content = content.strip()
        
        data = json.loads(content)
        
        # Write response to file for debugging after safe decoding
        with open("response.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))
        
        markers = []
        # Navigate the SIRI response structure
        # Siri -> ServiceDelivery -> VehicleMonitoringDelivery -> VehicleActivity
        if 'Siri' in data and 'ServiceDelivery' in data['Siri']:
            delivery = data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery']
            for activity in delivery.get('VehicleActivity', []):
                journey = activity.get('MonitoredVehicleJourney', {})
                location = journey.get('VehicleLocation', {})
                
                if 'Latitude' in location and 'Longitude' in location:
                    lat = float(location['Latitude'])
                    lon = float(location['Longitude'])
                    bearing = float(journey.get('Bearing', 0.0))
                    markers.append((lat, lon, bearing))
        
        return markers
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def main():
    # Get API key from environment variable
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Error: API_KEY environment variable not set.")
        print("Please export your 511 API key: export API_KEY='your_key'")
        return

    # Get map center from environment variable
    map_center_str = os.getenv("MAP_CENTER")
    map_center = None # Defaults to a bounding box of markers
    if map_center_str:
        try:
            map_center = [float(x.strip()) for x in map_center_str.split(',')]
        except ValueError:
            print("Warning: Invalid MAP_CENTER format in .env. Using default.")

    print("Fetching vehicle locations for agency 'SF' (Muni)...")
    markers = get_vehicle_locations(api_key, agency="SF")
    print(f"Found {len(markers)} vehicles.")
    
    if markers:
        print("Rendering map to sf_buses.png...")
        render_clean_map(markers, "sf_buses.png", zoom=14 if map_center else None, center=map_center)
    else:
        print("No vehicles found. Check your API key or try again later.")

if __name__ == "__main__":
    main()
