# RouteForger

RouteForger is a delivery-route optimizer for the Tel Aviv District. It
geocodes real addresses, calculates travel times over OpenStreetMap roads, and
uses beam search to order package pickups and deliveries.

The project includes a FastAPI backend, a Leaflet frontend, automated tests,
and Docker Compose configuration.

## Features

- Real address geocoding and drivable road routes through OSMnx
- Pickup-before-delivery constraints
- Package deadlines and late-delivery tracking
- Beam-search route optimization
- Interactive map, stop sequence, route duration, and distance
- Request validation and structured API errors
- Dockerized frontend and backend

## Current scope

- One courier
- One or more packages
- Unlimited courier capacity
- Addresses inside the Tel Aviv District
- Static travel-time estimates without live traffic

Beam search keeps the optimizer practical for small scenarios, but it does not
guarantee the optimal route or guarantee finding every possible solution.

## Run with Docker

Requirements: Docker and internet access on the first run.

```bash
docker compose up --build
```

Then open:

- Application: <http://localhost:5500>
- API documentation: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/health>

## Local development

Requires Python 3.11 or newer.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
uvicorn routeforger.api.app:app --reload --port 8000
```

Run the tests with:

```bash
pytest
```

## API

Calculate a route:

```http
POST /api/routes
Content-Type: application/json
```

Example request:

```json
{
  "couriers": [
    {
      "id": 1,
      "start_address": "Azrieli Center, Tel Aviv",
      "start_time": 21600
    }
  ],
  "packages": [
    {
      "id": 1,
      "source_address": "Dizengoff Center, Tel Aviv",
      "destination_address": "Bialik 20, Ramat Gan",
      "deadline": 32400
    }
  ]
}
```

Times are seconds since midnight. The response includes route geometry,
ordered stops, arrival times, total distance and duration, and each package's
deadline status.

## How it works

1. FastAPI validates the scenario.
2. OSMnx maps addresses to road-network nodes.
3. NetworkX calculates travel costs between relevant stops.
4. Beam search selects a pickup and delivery order.
5. The result is expanded into road geometry and displayed with Leaflet.

## Project structure

```text
backend/src/routeforger/   FastAPI, domain models, routing, and optimization
backend/tests/             Backend test suite
frontend/                  Leaflet browser interface
data/scenario.json         Example command-line input
compose.yml                Docker Compose configuration
```

The file-based workflow is also available with:

```bash
python -m routeforger.main
```
