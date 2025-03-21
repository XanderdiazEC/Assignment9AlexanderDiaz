import requests
import json

directions_api = "https://api.openrouteservice.org/v2/directions/driving-car"
geocode_api = "https://api.openrouteservice.org/geocode/search"
key = "5b3ce3597851110001cf6248bb5e17ee00824c7d9245b58a246ffdc1"  

def geocode_address(address):
    params = {
        "api_key": key,
        "text": address
    }
    response = requests.get(geocode_api, params=params)
    if response.status_code == 200:
        json_data = response.json()
        if json_data["features"]:
            coords = json_data["features"][0]["geometry"]["coordinates"]
            print(f"Geocoded coordinates for '{address}': {coords}")  
            if -90 <= coords[1] <= 90 and -180 <= coords[0] <= 180:
                return coords
            else:
                print(f"Error: Invalid coordinates for address '{address}'")
                return None
        else:
            print(f"Error: No results found for address '{address}'")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def format_time(seconds):
    """Convert seconds to a more readable format (hours, minutes)"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

def format_distance(meters):
    """Convert meters to kilometers or miles"""
    km = meters / 1000
    miles = km * 0.621371
    return f"{km:.1f} km ({miles:.1f} miles)"

def main():
    while True:
        orig = input("Starting Location: ")
        if orig.lower() in ["quit", "q"]:
            break
        
        dest = input("Destination: ")
        if dest.lower() in ["quit", "q"]:
            break
            
        
        orig_coords = geocode_address(orig)
        dest_coords = geocode_address(dest)

        if not orig_coords or not dest_coords:
            print("Unable to geocode one or both addresses. Please try again.\n")
            continue

        
        body = {
            "coordinates": [orig_coords, dest_coords]
        }

       
        headers = {
            "Authorization": key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(directions_api, headers=headers, json=body)
            response.raise_for_status()  
            
            json_data = response.json()
            
            if 'routes' in json_data and json_data['routes']:
                route = json_data['routes'][0]
                if 'segments' in route and route['segments']:
                    segment = route['segments'][0]
                    print("\nAPI Status: Successful route call.\n")
                    print("=============================================")
                    print(f"Directions from {orig} to {dest}")

                    
                    duration = segment.get('duration', 0)
                    distance = segment.get('distance', 0)

                    print(f"Trip Duration: {format_time(duration)}")
                    print(f"Distance: {format_distance(distance)}")
                    print("=============================================")

                    
                    if 'steps' in segment:
                        print("Step-by-Step Directions:")
                        for i, step in enumerate(segment['steps'], 1):
                            instruction = step.get('instruction', 'N/A')
                            step_distance = step.get('distance', 0)
                            print(f"{i}. {instruction} ({step_distance:.0f} meters)")
                    else:
                        print("No step-by-step directions available.")

                    print("=============================================\n")
                else:
                    print("Error: No segments found in the route.")
            else:
                print("Error: No routes found in the response.")
                
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")

if __name__ == "__main__":
    main()
