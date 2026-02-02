"""
FastAPI Main Application
========================
This module defines the main FastAPI application for the Real-Time Supply Chain Tracker.
It provides:
- REST API endpoints for general health checks
- WebSocket endpoint for real-time flight/shipment data streaming
- CORS middleware for frontend communication
- Integration with Redpanda/Kafka for message consumption
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaConsumer
import json
import asyncio

# Initialize FastAPI application
app = FastAPI(
    title="Real-Time Supply Chain Tracker API",
    description="Backend API for tracking flights and shipments in real-time",
    version="1.0.0"
)

# ============================================================================
# CORS Middleware Configuration
# ============================================================================
# Allows the frontend React application to communicate with this backend API.
# In production, replace "*" with specific allowed origins for security.
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],   # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# ============================================================================
# Health Check Endpoint
# ============================================================================
# Simple endpoint to verify the backend is running and accessible.
# Returns a JSON response indicating the API is alive.
# ============================================================================
@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    
    Returns:
        dict: A message confirming the backend is running
    """
    return {"message": "Backend is ALIVE! Go to /docs to see endpoints."}

# ============================================================================
# WebSocket Endpoint for Real-Time Data Streaming
# ============================================================================
# Establishes a WebSocket connection that streams flight/shipment data
# from Redpanda/Kafka topics to connected frontend clients in real-time.
# 
# Flow:
#   1. Client connects via WebSocket
#   2. Backend connects to Redpanda consumer
#   3. Messages from 'shipments' topic are forwarded to client
#   4. Connection closes when client disconnects or error occurs
# ============================================================================
@app.websocket("/ws/flights")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time flight/shipment tracking.
    
    This endpoint:
    - Accepts WebSocket connections from frontend
    - Subscribes to 'shipments' topic in Redpanda/Kafka
    - Forwards messages from Kafka to WebSocket clients
    - Handles connection errors gracefully
    
    Args:
        websocket: WebSocket connection object from FastAPI
    """
    # Accept the WebSocket connection from client
    await websocket.accept()
    
    # Connect to Redpanda (Kafka-compatible broker)
    # - 'shipments': Topic name where flight data is published
    # - 'redpanda:29092': Internal Docker network address
    # - 'frontend-dashboard': Consumer group ID for load balancing
    consumer = AIOKafkaConsumer(
        'shipments',
        bootstrap_servers='redpanda:29092',
        group_id="frontend-dashboard"
    )
    
    # Start the Kafka consumer
    await consumer.start()
    
    try:
        # Continuous loop: Read messages from Kafka and forward to WebSocket
        # Each message from the 'shipments' topic is:
        #   1. Decoded from bytes to string
        #   2. Parsed as JSON
        #   3. Sent to the connected WebSocket client
        async for msg in consumer:
            data = json.loads(msg.value.decode('utf-8'))
            await websocket.send_json(data)
    except Exception as e:
        # Log errors but don't crash - allows for graceful error handling
        print(f"WebSocket Error: {e}")
    finally:
        # Always stop the consumer when connection closes
        await consumer.stop()
        