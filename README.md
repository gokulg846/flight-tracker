# ✈️ Real-Time Flight Tracker

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)
![Python](https://img.shields.io/badge/python-3.9-3776AB.svg?style=flat&logo=python&logoColor=white)
![Redpanda](https://img.shields.io/badge/Redpanda-Kafka-orange)

**A high-performance, event-driven simulation that tracks flights in real-time across a distributed system.**

---

## 📖 About The Project

I built this project to move beyond standard CRUD apps and dive into **Event-Driven Architecture**.

The goal was to answer a simple question: *How do companies like Uber or FlightAware track moving assets instantly?*

The solution is a pipeline that generates simulated telemetry data, streams it through a high-throughput message broker (Redpanda), and pushes updates to a React frontend via WebSockets. The entire stack is containerized, meaning it spins up with a single command.

### ⚡ Key Features
* **Real-Time Visualization:** Smooth, moving markers on an interactive Leaflet map.
* **Event Streaming:** Uses **Redpanda** (a drop-in Kafka replacement) to handle high-volume data ingestion.
* **Instant Updates:** Replaces slow polling (HTTP GET) with **WebSockets** for millisecond latency.
* **Fault Tolerance:** The producer and consumer are decoupled; if the frontend closes, the backend keeps processing.
* **Dockerized:**

---

## 🛠️ Tech Stack

* **Ingestion:** Python (Simulated Producer)
* **Broker:** Redpanda (Kafka Protocol)
* **Backend:** FastAPI (Python, AsyncIO)
* **Frontend:** React (TypeScript, Leaflet.js)
* **Infrastructure:** Docker & Docker Compose

---

## 🏗️ Architecture

Data flows through the system in a unidirectional pipeline:

```mermaid
graph LR
    P[Producer] -- JSON Stream --> B[Redpanda (Kafka)]
    B -- Async Consumer --> S[FastAPI Backend]
    S -- WebSocket Push --> C[React Frontend]
