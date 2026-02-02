"""
Mock Flight Data Producer
==========================
This script generates fake flight data for testing purposes without requiring
the OpenSky API. Useful for:
- Testing the frontend map visualization
- Development when OpenSky API is unavailable
- Demonstrating the system with predictable test data

Generates 5 fake flights near New York City coordinates and sends them
as a batch to the 'shipments' topic every 2 seconds.

Usage:
    Run this script instead of producer.py for testing with mock data.
    Ensure Redpanda is running and accessible at localhost:9092.
"""

import time
import json
import random
from kafka import KafkaProducer  # Standard kafka-python library

# ============================================================================
# Kafka/Redpanda Producer Configuration
# ============================================================================
# Connects to Redpanda broker and serializes messages as JSON.
# ============================================================================
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Use external port for local script
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # JSON serialization
)

print("Started generating fake flights...")

# ============================================================================
# Mock Data Generation Loop
# ============================================================================
# Continuously generates fake flight data and publishes to Kafka/Redpanda.
# Creates 5 test flights with random positions near New York City.
# ============================================================================
while True:
    # Generate 5 fake flights with random positions
    flights = []
    for i in range(5):
        flights.append({
            "callsign": f"TEST-{i}",                                    # Test callsign
            "longitude": -74.0060 + random.uniform(-0.5, 0.5),         # Near NYC (Manhattan)
            "latitude": 40.7128 + random.uniform(-0.5, 0.5),          # Near NYC (Manhattan)
            "velocity": random.randint(100, 300),                      # Random velocity (km/h)
            "true_track": random.randint(0, 360)                       # Random heading (degrees)
        })

    # Send all flights as a single batch message to the 'shipments' topic
    # Note: This sends a list, which the consumer must handle accordingly
    producer.send('shipments', flights)
    print(f"Sent {len(flights)} fake flights.")
    
    # Wait 2 seconds before generating next batch (simulates real-time updates)
    time.sleep(2)