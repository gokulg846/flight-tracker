/**
 * Real-Time Flight Tracking Map Component
 * =========================================
 * This React component displays a real-time map of flights/shipments using Leaflet.
 * It connects to the backend WebSocket endpoint to receive live flight data updates
 * and renders them as markers on an interactive map.
 * 
 * Features:
 * - WebSocket connection for real-time updates
 * - Interactive map with zoom and pan
 * - Flight markers with popup information
 * - Handles both single objects and arrays of flights
 * - Color-coded markers (UPS = gold, others = red)
 */

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

/**
 * FlightData Interface
 * ====================
 * Defines the structure of flight/shipment data received from the backend.
 * Some fields are optional to accommodate different data sources (OpenSky vs mock data).
 */
interface FlightData {
  callsign: string;        // Flight callsign (e.g., "UPS123", "FDX456")
  latitude: number;         // Latitude coordinate (required)
  longitude: number;        // Longitude coordinate (required)
  velocity: number;         // Velocity in km/h (required)
  true_track?: number;      // Heading/bearing in degrees (optional)
  altitude?: number;        // Altitude in meters (optional)
  icao24?: string;         // Unique aircraft identifier (optional, mock data may not have it)
}

/**
 * Main App Component
 * ==================
 * Manages WebSocket connection and flight state, renders the interactive map.
 */
function App() {
  // State: Dictionary of flights keyed by ID (icao24 or callsign)
  // Using dictionary allows efficient updates and prevents duplicate markers
  const [flights, setFlights] = useState({} as { [key: string]: FlightData });

  /**
   * WebSocket Connection Effect
   * ============================
   * Establishes WebSocket connection to backend on component mount.
   * Receives real-time flight data and updates state accordingly.
   * Cleans up connection on component unmount.
   */
  useEffect(() => {
    // Connect to backend WebSocket endpoint
    // Use 'ws://' protocol for localhost (not 'wss://' which requires SSL)
    const ws = new WebSocket("ws://localhost:8000/ws/flights");

    // Connection opened successfully
    ws.onopen = () => {
      console.log("Connected to Real-Time Stream!");
    };

    // Handle incoming messages from WebSocket
    ws.onmessage = (event) => {
      try {
        // Parse JSON data from WebSocket message
        const parsed = JSON.parse(event.data);
        
        // Handle both array and single object formats:
        // - Array: Multiple flights sent as batch (from mock_producer.py)
        // - Object: Single flight (from producer.py)
        const incomingFlights = Array.isArray(parsed) ? parsed : [parsed];

        // Update flights state with new data
        setFlights(prev => {
          const newFlights = { ...prev };
          
          // Process each incoming flight
          incomingFlights.forEach((flight: FlightData) => {
            // Use icao24 as unique ID if available, otherwise use callsign
            // This handles cases where mock data doesn't have icao24
            const id = flight.icao24 || flight.callsign;
            if (id) {
              // Update or add flight to dictionary
              newFlights[id] = flight;
            }
          });
          
          return newFlights;
        });

      } catch (err) {
        // Handle JSON parsing errors gracefully
        console.error("Error parsing flight data", err);
      }
    };

    // Connection closed
    ws.onclose = () => console.log("Disconnected");

    // Cleanup: Close WebSocket when component unmounts
    return () => {
      ws.close();
    };
  }, []);  // Empty dependency array: run only on mount

  /**
   * Render Map Component
   * ====================
   * Renders an interactive Leaflet map with flight markers.
   * Each flight is displayed as a colored circle marker with a popup.
   */
  return (
    <div style={{ height: "100vh", width: "100vw" }}>
      {/* Map centered on New York City coordinates for test data visualization */}
      <MapContainer 
        center={[40.7128, -74.0060]}  // NYC coordinates (latitude, longitude)
        zoom={10}                      // Initial zoom level
        style={{ height: "100%", width: "100%" }}
      >
        {/* Dark theme tile layer from CartoDB */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        
        {/* Render flight markers for each flight in state */}
        {Object.values(flights).map((flight) => (
          <CircleMarker 
            // Use icao24 or callsign as React key for efficient rendering
            key={flight.icao24 || flight.callsign}
            // Marker position from flight coordinates
            center={[flight.latitude, flight.longitude]}
            radius={6}  // Marker size in pixels
            pathOptions={{ 
              // Color coding: UPS flights = gold, others = red
              color: flight.callsign.startsWith("UPS") ? "#ffcc00" : "#ff0000", 
              fillOpacity: 0.8,    // Marker fill opacity
              fillColor: "red"     // Fill color
            }}
          >
            {/* Popup shown when marker is clicked */}
            <Popup>
              <div style={{ color: "black" }}>
                <strong>{flight.callsign}</strong><br/>
                Speed: {flight.velocity} km/h
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}

export default App;