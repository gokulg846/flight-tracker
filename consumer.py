"""
Kafka/Redpanda Consumer
=======================
This script consumes messages from the 'shipments' topic and prints them
to the console. Useful for debugging and verifying that producers are
sending data correctly.

This is a simple test consumer that demonstrates how to read from Kafka/Redpanda.
The main application uses aiokafka in the FastAPI backend for WebSocket streaming.

Usage:
    Run this script to monitor messages being published to the 'shipments' topic.
    Ensure Redpanda is running and accessible at localhost:9092.
"""

from kafka import KafkaConsumer
import json

# ============================================================================
# Kafka/Redpanda Consumer Configuration
# ============================================================================
# Subscribes to the 'shipments' topic and deserializes JSON messages.
# - auto_offset_reset='latest': Only read new messages (ignore old ones)
# - value_deserializer: Automatically converts JSON bytes to Python dict
# ============================================================================
consumer = KafkaConsumer(
    'shipments',                                    # Topic name
    bootstrap_servers=['localhost:9092'],          # External port for local scripts
    auto_offset_reset='latest',                    # Start from latest messages
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # JSON deserialization
)

print("🎧 Listening for shipments...")

# ============================================================================
# Message Consumption Loop
# ============================================================================
# Continuously reads messages from the 'shipments' topic and prints them.
# Handles both single flight objects and lists of flights.
# ============================================================================
for msg in consumer:
    flight_data = msg.value
    
    # Handle different message formats:
    # - List: Multiple flights sent as a batch (from mock_producer.py)
    # - Dict: Single flight object (from producer.py)
    if isinstance(flight_data, list):
        # It's a list, so loop through each flight
        for flight in flight_data:
            print(f"Received: {flight['callsign']} at {flight['latitude']}, {flight['longitude']}")
    else:
        # It's a single flight object
        print(f"Received: {flight_data['callsign']} at {flight_data['latitude']}, {flight_data['longitude']}")