RouteForger

RouteForger is a small urban package-delivery route optimizer built around real geographic locations and road networks.

The first version focuses on a deliberately simple problem:

Given one courier and a predefined list of packages, calculate an efficient route that picks up and delivers every package while considering delivery deadlines.

V1 Scope
One courier
Unlimited courier capacity
Package weight ignored
All packages known in advance
Packages loaded from a JSON file
Input validation with Pydantic
Real source/destination addresses
Address geocoding
Real road travel times/distances
Route optimization
Interactive map visualization

Dynamic events, multiple couriers, capacity constraints, and manual package creation are intentionally left for later versions.

Input

A delivery scenario is initially loaded from:

data/packages.json

Example:

{
  "courier_start": "Azrieli Center, Tel Aviv",
  "packages": [
    {
      "id": 1,
      "source": "Dizengoff 100, Tel Aviv",
      "destination": "Bialik 20, Ramat Gan",
      "deadline": "2026-08-11T14:00:00"
    }
  ]
}

The JSON is parsed and validated before entering the routing logic.

Application Flow
packages.json
     ↓
Parse + Validate
     ↓
DeliveryScenario
     ↓
Geocoding
     ↓
Road Routing Data
     ↓
Route Optimizer
     ↓
Optimized Route
     ↓
Frontend Map
Project Structure
routeforge/
│
├── backend/
│   ├── src/
│   │   └── routeforge/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       │
│   │       ├── domain/
│   │       │   ├── package.py
│   │       │   ├── courier.py
│   │       │   ├── route.py
│   │       │   └── scenario.py
│   │       │
│   │       ├── input/
│   │       │   └── json_loader.py
│   │       │
│   │       ├── services/
│   │       │   ├── geocoding.py
│   │       │   └── routing.py
│   │       │
│   │       ├── optimization/
│   │       │   └── optimizer.py
│   │       │
│   │       └── api/
│   │           └── # FastAPI added later
│   │
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── data/
│   └── packages.json
│
├── README.md
├── pyproject.toml
└── .gitignore
Architecture

The backend contains all delivery logic:

input parsing
validation
domain models
geocoding
road-routing integration
route optimization

The frontend is responsible only for visualization and future user interaction.

The optimizer should not depend on how packages were provided.

This allows future inputs such as:

JSON file ──────┐
FastAPI ────────┤
Manual UI ──────┼──► DeliveryScenario ► Optimizer
Map input ──────┘
Future Extensions

Possible later additions include:

FastAPI server
manual package entry
selecting pickup/delivery locations directly on the map
multiple couriers
package weight and courier capacity
dynamic package arrival
traffic-aware re-optimization
more advanced routing algorithms
Goal

The main engineering problem is:

Find a valid and efficient route through real-world pickup and delivery locations while respecting pickup-before-delivery constraints and delivery deadlines.