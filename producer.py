"""
OpenSky API Producer
====================
This script fetches real-time flight data from the OpenSky Network API,
filters for cargo flights (FedEx and UPS), and publishes them to Redpanda/Kafka.

The OpenSky Network provides free access to real-time flight tracking data
for research and hobby purposes. This producer:
1. Polls the OpenSky API every 20 seconds
2. Filters for cargo flights (FDX and UPS callsigns)
3. Publishes each flight as a message to the 'shipments' topic

Usage:
    Run this script to start producing flight data to Kafka/Redpanda.
    Ensure Redpanda is running and accessible at localhost:9092.
"""

import requests
import json
import time
from kafka import KafkaProducer  # pip install kafka-python

# ============================================================================
# Kafka/Redpanda Producer Configuration
# ============================================================================
# Connects to Redpanda broker running on localhost:9092 (external port).
# Messages are automatically serialized to JSON format.
# ============================================================================
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # External port for local scripts
    value_serializer=lambda x: json.dumps(x).encode('utf-8')  # JSON serialization
)

# ============================================================================
# OpenSky API Configuration
# ============================================================================
# OpenSky Network provides free, real-time flight tracking data.
# The '/states/all' endpoint returns all currently tracked flights globally.
# Free tier allows approximately 1 request every 10 seconds.
# ============================================================================
OPENSKY_URL = "https://opensky-network.org/api/states/all"

def get_cargo_flights():
    """
    Fetches flight data from OpenSky API and filters for cargo flights.
    
    Returns:
        list: List of flight dictionaries containing cargo flight data.
              Each flight dict contains: icao24, callsign, origin_country,
              longitude, latitude, velocity, altitude, timestamp.
              Returns empty list on error.
    """
    try:
        # Make HTTP GET request to OpenSky API
        response = requests.get(OPENSKY_URL)

        # Debug output: Check API response status
        print(f"Status Code: {response.status_code}")
        print(f"Raw Content: {response.text[:200]}")  # Print first 200 chars

        # Only parse JSON if request was successful
        if response.status_code == 200:
            data = response.json()
        else:
            print("Skipping... API returned an error.")
            data = {'states': []}  # Empty states to keep script running
        
        # Extract timestamp and flight states from API response
        current_time = data.get('time', 0)
        states = data.get('states', [])
        
        cargo_flights = []
        
        # Process each flight state
        # OpenSky API returns flights as arrays with fixed positions:
        # [0] = icao24, [1] = callsign, [2] = origin_country,
        # [5] = longitude, [6] = latitude, [9] = velocity, [13] = altitude
        if states:
            for flight in states:
                callsign = flight[1].strip() if flight[1] else ""
                
                # Filter: Only include FedEx (FDX) and UPS (UPS) cargo flights
                if callsign.startswith("FDX") or callsign.startswith("UPS"):
                    flight_data = {
                        "icao24": flight[0],           # Unique aircraft identifier
                        "callsign": callsign,           # Flight callsign (e.g., "UPS123")
                        "origin_country": flight[2],   # Country of origin
                        "longitude": flight[5],        # Longitude coordinate
                        "latitude": flight[6],         # Latitude coordinate
                        "velocity": flight[9],          # Velocity in m/s
                        "altitude": flight[13],        # Altitude in meters
                        "timestamp": current_time      # API response timestamp
                    }
                    cargo_flights.append(flight_data)
                    
        return cargo_flights

    except Exception as e:
        # Handle any errors gracefully and return empty list
        print(f"Error fetching data: {e}")
        return []

# ============================================================================
# Main Producer Loop
# ============================================================================
# Continuously fetches flight data and publishes to Kafka/Redpanda.
# Runs indefinitely until interrupted (Ctrl+C).
# ============================================================================
print("📡 Connected to OpenSky. Tracking Cargo Flights...")

while True:
    # Fetch cargo flights from OpenSky API
    flights = get_cargo_flights()
    
    if flights:
        print(f"✈️  Found {len(flights)} active Cargo flights. Sending to Kafka...")
        
        # Send each flight as a separate message to the 'shipments' topic
        # Each message will be consumed by the backend WebSocket handler
        for flight in flights:
            producer.send('shipments', value=flight)
            
    else:
        print("Waiting for data...")
 
    # Rate limiting: OpenSky free tier allows roughly 1 request every 10 seconds
    # Using 20 seconds to be safe and avoid rate limiting
    time.sleep(20)