# Urban Package Delivery Route Optimizer

## 1. Project Overview

This project is a small delivery-routing application operating over a real-world geographic area, initially focused on the **Tel Aviv metropolitan area**.

The application allows a user to create packages using real source and destination addresses. Each package also has a delivery deadline.

A single courier must collect and deliver all packages while following the real road network.

The main goal of the system is to calculate a valid and efficient delivery route while attempting to meet package deadlines.

This project is intentionally designed as a simple first version that can later be expanded with multiple couriers, capacities, live events, traffic data, and more advanced optimization.

---

# 2. MVP Scope

Version 1 contains:

* One courier.
* A fixed set of packages.
* All packages are known before route calculation begins.
* Packages have no weight.
* Courier has unlimited carrying capacity.
* Real source and destination addresses.
* Real geographic map.
* Real road/street routing.
* Package delivery deadlines.
* Route calculation.
* Visualization of the calculated route.

There are no dynamic events once route calculation starts.

---

# 3. Main Use Case

The user creates several packages.

Example:

```text
Package 1
Source: Dizengoff St 50, Tel Aviv
Destination: Abba Hillel St 10, Ramat Gan
Deadline: 14:00

Package 2
Source: Rothschild Blvd 20, Tel Aviv
Destination: Weizmann St 30, Givatayim
Deadline: 15:00
```

The user then requests route calculation.

The system:

1. Converts addresses into geographic coordinates.
2. Determines travel distances/times between relevant locations.
3. Calculates a valid pickup/delivery order.
4. Attempts to satisfy delivery deadlines.
5. Produces the final courier route.
6. Displays the route on a map.

---

# 4. Core Domain Objects

## Package

A package represents one delivery request.

Suggested fields:

```text
id
source_address
source_latitude
source_longitude

destination_address
destination_latitude
destination_longitude

deadline

status
```

Possible package statuses:

```text
WAITING
PICKED_UP
DELIVERED
```

For the initial MVP, status tracking may be simplified if necessary.

---

## Courier

Version 1 contains exactly one courier.

Suggested fields:

```text
id
starting_location
latitude
longitude
```

The courier has:

```text
capacity = unlimited
```

Package weight is ignored.

---

## Route Stop

A calculated courier route consists of ordered stops.

Example:

```text
1. Courier starting point
2. Pick up Package 3
3. Pick up Package 1
4. Deliver Package 3
5. Pick up Package 2
6. Deliver Package 1
7. Deliver Package 2
```

Each route stop should contain information such as:

```text
package_id
stop_type
address
latitude
longitude
estimated_arrival_time
```

Where:

```text
stop_type = PICKUP | DELIVERY
```

---

# 5. Routing Rules

Every generated route must satisfy the following rules.

## Rule 1 — Pickup Before Delivery

A package must always be collected before it can be delivered.

Valid:

```text
Pickup P1
...
Deliver P1
```

Invalid:

```text
Deliver P1
...
Pickup P1
```

---

## Rule 2 — Every Package Must Be Processed

Every package must have:

```text
exactly one pickup
exactly one delivery
```

---

## Rule 3 — Single Courier

All packages are handled by the same courier.

---

## Rule 4 — Unlimited Capacity

The courier may carry any number of packages simultaneously.

No weight or vehicle-capacity calculations are required.

---

## Rule 5 — Deadlines

The optimizer should attempt to deliver each package before its deadline.

A route that misses fewer deadlines should generally be considered better than one that misses more deadlines.

The exact optimization strategy may evolve during development.

---

# 6. Optimization Problem

The central algorithmic problem is:

> Given one courier, N packages, pickup locations, delivery locations, travel times, and package deadlines, find an efficient valid route.

A valid route must respect pickup-before-delivery constraints.

The optimization should initially consider:

```text
1. Number of missed deadlines
2. Total lateness
3. Total route travel time/distance
```

A possible priority order is:

```text
First: minimize missed deadlines
Second: minimize total lateness
Third: minimize total route time
```

The first implementation does not need to produce the mathematically optimal route.

A reasonable heuristic solution is acceptable.

The optimization algorithm should ideally be isolated from the API and UI so it can later be replaced or improved.

---

# 7. Real-World Map

The application should use a real geographic map.

Initial operating region:

```text
Tel Aviv metropolitan area
```

The application should be able to display:

* Courier starting location.
* Package pickup locations.
* Package delivery locations.
* Calculated route.
* Ordered route stops.

Possible map libraries include:

```text
Leaflet
MapLibre
OpenStreetMap-based solutions
```

The frontend technology can remain intentionally simple.

---

# 8. Geocoding

Users provide normal addresses rather than coordinates.

Example:

```text
"Ibn Gabirol 71, Tel Aviv"
```

The system should use a geocoding service to convert the address into:

```text
latitude
longitude
```

The application should store the resulting coordinates so that the same address does not need to be repeatedly geocoded.

---

# 9. Road Routing

Straight-line geographic distance is not sufficient.

Travel calculations should eventually use the actual road network.

The routing component should provide information such as:

```text
distance(A, B)
travel_time(A, B)
route_geometry(A, B)
```

This component should be abstracted behind a service/interface so the routing provider can later be replaced.

Conceptually:

```text
RoutingService

get_route(source, destination)
get_distance(source, destination)
get_travel_time(source, destination)
```

---

# 10. Backend API

Suggested backend:

```text
Python
FastAPI
```

Initial API endpoints may look approximately like:

```text
POST   /packages
GET    /packages
GET    /packages/{id}
DELETE /packages/{id}
```

Route operations:

```text
POST /route/calculate
GET  /route
```

Optional:

```text
DELETE /packages
```

to reset the simulation.

Exact endpoint names are not important and may change during development.

---

# 11. Example Package Request

```json
{
    "source_address": "Dizengoff Street 50, Tel Aviv",
    "destination_address": "Abba Hillel Street 10, Ramat Gan",
    "deadline": "2026-08-10T14:00:00"
}
```

The backend may enrich it with coordinates after geocoding.

Example internal representation:

```json
{
    "id": 1,
    "source_address": "Dizengoff Street 50, Tel Aviv",
    "source_latitude": 32.078,
    "source_longitude": 34.774,
    "destination_address": "Abba Hillel Street 10, Ramat Gan",
    "destination_latitude": 32.084,
    "destination_longitude": 34.802,
    "deadline": "2026-08-10T14:00:00"
}
```

---

# 12. Database

Recommended database:

```text
PostgreSQL
```

PostGIS may be added if useful for geographic operations.

For the initial version, the database mainly stores:

```text
packages
courier/start location
calculated routes
route stops
```

The application should avoid unnecessary complexity in the database design.

---

# 13. Suggested Architecture

A simple layered structure is preferred.

Example:

```text
app/
│
├── main.py
│
├── api/
│   ├── packages.py
│   └── routes.py
│
├── models/
│   ├── package.py
│   └── route.py
│
├── schemas/
│   ├── package.py
│   └── route.py
│
├── services/
│   ├── geocoding_service.py
│   ├── routing_service.py
│   └── optimization_service.py
│
├── repositories/
│   └── package_repository.py
│
└── db/
    ├── database.py
    └── models.py
```

This is only a suggested structure.

Do not create abstractions that are not yet useful.

---

# 14. Important Design Separation

Three problems should remain separate.

## Geographic Routing

Answers:

> How long does it take to travel from location A to B?

---

## Delivery Optimization

Answers:

> In which order should the courier visit all pickup and delivery locations?

---

## Visualization

Answers:

> How should the resulting route be displayed to the user?

These components should not depend heavily on each other's implementation details.

---

# 15. Development Milestones

## Milestone 1 — Basic Backend

Create:

* FastAPI project.
* Package model/schema.
* Package CRUD.
* Simple storage/database.
* Courier starting position.

No map and no optimizer yet.

Success condition:

> Packages can be created and retrieved through the API.

---

## Milestone 2 — Geocoding

Add address-to-coordinate conversion.

When a package is created:

```text
address
    ↓
geocoding service
    ↓
latitude + longitude
```

Success condition:

> Every valid package has geographic coordinates.

---

## Milestone 3 — Map Interface

Create a simple frontend displaying:

* Tel Aviv metro map.
* Pickup markers.
* Destination markers.
* Courier starting point.

Success condition:

> Packages added through the API appear correctly on the real map.

---

## Milestone 4 — Point-to-Point Routing

Connect the application to a road-routing service.

Given:

```text
Location A
Location B
```

retrieve:

```text
travel distance
travel time
route geometry
```

Success condition:

> The application can display a real driving route between two locations.

---

## Milestone 5 — Simple Delivery Algorithm

Implement the first delivery-order algorithm.

It does not need to be optimal.

Possible first approaches:

* earliest-deadline heuristic
* nearest valid stop
* combination of distance and deadline

Success condition:

> The algorithm always produces a valid route where every package is picked up before delivery.

---

## Milestone 6 — Better Optimization

Improve the algorithm so that it considers:

* deadlines
* geographic distance
* travel time
* lateness

Compare different algorithms/heuristics.

Success condition:

> The system produces noticeably better routes than naive approaches.

---

## Milestone 7 — Full Route Visualization

Display the complete optimized courier route.

Example:

```text
Depot
  ↓
Pickup P2
  ↓
Pickup P1
  ↓
Deliver P2
  ↓
Pickup P3
  ↓
Deliver P1
  ↓
Deliver P3
```

Show useful information such as:

```text
total route distance
estimated completion time
packages delivered on time
late packages
```

Success condition:

> A user can visually understand the optimizer's decision from the map.

---

# 16. Testing

Important algorithm tests should include:

### Pickup constraint

```text
pickup(P1) must occur before delivery(P1)
```

### Completeness

Every package appears exactly twice:

```text
one pickup
one delivery
```

### Empty input

```text
0 packages
```

should produce a valid empty route.

### Single package

The expected route should be:

```text
courier
→ pickup
→ delivery
```

### Deadline tests

Create scenarios where:

* every deadline can be satisfied
* one deadline cannot be satisfied
* several routes exist with different lateness

---

# 17. Non-Goals for Version 1

The following features should NOT be implemented initially:

* Multiple couriers.
* Package weight.
* Courier capacity.
* Dynamic package arrival.
* Live courier GPS.
* Real-time traffic events.
* Courier breakdowns.
* Redis.
* Kafka/RabbitMQ.
* Microservices.
* Machine learning.
* LLM integration.
* Mobile application.
* Payments.
* User authentication.
* Complex role management.

These may be considered only after the MVP is complete.

---

# 18. Possible Future Extensions

After Version 1 works correctly, possible upgrades include:

### Multiple Couriers

Assign packages between several delivery vehicles.

### Capacity

Add:

```text
package.weight
courier.capacity
```

### Dynamic Packages

Allow new deliveries to enter while couriers are already operating.

### Live Traffic

Change travel times according to traffic conditions.

### Re-optimization

Recalculate routes when circumstances change.

### Courier Simulation

Animate courier movement along the road network.

### PostGIS

Use spatial database queries for geographic operations.

### Advanced Optimization

Explore algorithms such as:

* local search
* simulated annealing
* genetic algorithms
* constraint programming
* OR-Tools

---

# 19. MVP Definition of Done

Version 1 can be considered complete when:

1. A user can add packages using real addresses.
2. Addresses are converted into coordinates.
3. Packages appear on a real map.
4. One courier has a defined starting location.
5. The system knows road travel time/distance between locations.
6. The optimizer creates a valid pickup/delivery sequence.
7. Package deadlines influence route selection.
8. The calculated route is displayed on the map.
9. The application reports route statistics.
10. The project has automated tests for its main routing constraints.

---

# 20. Project Philosophy

Keep the first version simple.

The objective is not to simulate an entire logistics company.

The objective is to build a clean application around one interesting engineering problem:

> **How should one courier efficiently collect and deliver a predefined set of packages across a real city while respecting delivery deadlines?**

Once this problem is implemented well, more complex logistics features can be added incrementally.
