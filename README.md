# Grid Monitor ⚡

A full-stack Dockerized application that monitors and visualizes real-time electricity generation across Sweden's energy zones (SE1, SE2, SE3, SE4). 

## Architecture
* **Backend:** FastAPI (Python) fetching real-time data from the Svenska kraftnät (SVK) API. Includes a live simulation fallback mechanism.
* **Frontend:** React + Vite utilizing Chart.js for responsive data visualization.
* **Infrastructure:** Fully containerized using Docker and Docker Compose for seamless local and production deployments.

## Local Development
To run the application locally on your machine:
1. Ensure Docker Desktop is running.
2. Open your terminal in the project root and run:
   ```bash
   docker compose up -d --build