# RouteForge V1 Roadmap

Use the checkboxes in this document to track progress. Complete each milestone's
definition of done before moving to the next milestone.

## Milestone 1: Project foundation

**Goal:** Establish a clean, runnable project.

- [x] Create the `backend/src/routeforge` package structure.
- [x] Add project configuration in `pyproject.toml`.
- [x] Add a sample delivery scenario.
- [ ] Add initial automated tests.
- [ ] Create and activate a virtual environment.
- [ ] Install the project with `pip install -e ".[dev]"`.
- [ ] Confirm that `pytest` passes in a fresh environment.
- [ ] Confirm that the `routeforge` command loads the sample scenario.

**Definition of done:**

- [ ] The project installs successfully.
- [ ] All tests pass.
- [ ] The CLI loads `data/packages.json`.

## Milestone 2: Input validation

**Goal:** Reliably reject invalid delivery scenarios.

- [ ] Validate required package fields.
- [ ] Require positive, unique package IDs.
- [ ] Reject blank addresses.
- [ ] Parse deadlines into datetime values.
- [ ] Add clear handling for missing or unreadable files.
- [ ] Add clear handling for malformed JSON.
- [ ] Add tests for every invalid input case.

**Definition of done:**

- [ ] Valid input becomes a `DeliveryScenario`.
- [ ] Invalid input produces a clear error.
- [ ] Expected input edge cases have automated tests.

## Milestone 3: Geocoding

**Goal:** Convert every address into geographic coordinates.

- [ ] Choose and document a geocoding provider.
- [ ] Implement the `Geocoder` interface.
- [ ] Add request timeouts and useful provider errors.
- [ ] Cache results to avoid repeated requests.
- [ ] Detect addresses that cannot be resolved.
- [ ] Mock the provider in unit tests.

**Definition of done:**

- [ ] Courier, pickup, and delivery addresses receive coordinates.
- [ ] Provider failures are handled cleanly.
- [ ] Unit tests do not require internet access.

## Milestone 4: Road-routing data

**Goal:** Obtain real driving distances and travel times.

- [ ] Choose and document a road-routing provider.
- [ ] Implement the `RoadRouter` interface.
- [ ] Build a travel-time and distance matrix.
- [ ] Validate incomplete or invalid provider responses.
- [ ] Add timeout and failure handling.
- [ ] Test with mocked routing responses.

**Definition of done:**

- [ ] Travel costs can be calculated between all scenario locations.
- [ ] The optimizer receives provider-independent routing data.
- [ ] External failures produce understandable errors.

## Milestone 5: Valid route generation

**Goal:** Always create a route that obeys delivery constraints.

- [ ] Represent pickup and delivery stops.
- [ ] Provide a deterministic baseline route.
- [ ] Guarantee pickup occurs before delivery.
- [ ] Include the courier's starting location in route calculations.
- [ ] Ensure every package appears exactly twice.
- [ ] Calculate total distance and duration.
- [ ] Expand route-validity tests.

**Definition of done:**

- [ ] Every valid scenario produces a valid route.
- [ ] No delivery occurs before its pickup.
- [ ] Every package is picked up and delivered exactly once.

## Milestone 6: Route optimization

**Goal:** Improve routes using real travel costs and deadlines.

- [ ] Implement a simple nearest-valid-stop heuristic.
- [ ] Consider deadlines when choosing the next stop.
- [ ] Track estimated arrival times.
- [ ] Report missed deadlines.
- [ ] Compare optimized routes with the baseline.
- [ ] Keep optimization independent of input and provider details.

**Definition of done:**

- [ ] Every optimized route remains valid.
- [ ] Optimized cost is usually lower than the baseline cost.
- [ ] Deadline decisions are deterministic and tested.
- [ ] Missed deadlines are clearly reported.

V1 does not require a mathematically perfect solution. A clear, well-tested
heuristic is sufficient.

## Milestone 7: Route output format

**Goal:** Produce data that the frontend can visualize.

- [ ] Define a serializable route-result model.
- [ ] Include ordered stops and coordinates.
- [ ] Include package IDs and stop types.
- [ ] Include distance, duration, and arrival times.
- [ ] Include deadline status.
- [ ] Export route results as JSON.

**Definition of done:**

- [ ] One command generates a complete route-result JSON file.
- [ ] The frontend can consume it without backend-specific knowledge.

## Milestone 8: Interactive map

**Goal:** Display the optimized route visually.

- [ ] Set up a map using Leaflet or a similar library.
- [ ] Show the courier's starting point.
- [ ] Use distinct pickup and delivery markers.
- [ ] Draw the route geometry.
- [ ] Display ordered stop information.
- [ ] Show route totals and deadline warnings.

**Definition of done:**

- [ ] Opening the frontend displays the complete scenario.
- [ ] Route order is visually clear.
- [ ] Pickup, delivery, and deadline states are distinguishable.

## Milestone 9: End-to-end workflow

**Goal:** Connect the complete application through one documented workflow.

```text
packages.json
  -> validation
  -> geocoding
  -> road-routing matrix
  -> optimization
  -> result JSON
  -> map
```

- [ ] Connect all backend components.
- [ ] Add one command for generating a route.
- [ ] Add an end-to-end test with mocked external services.
- [ ] Provide a useful error when any stage fails.
- [ ] Update the README with setup and usage instructions.

**Definition of done:**

- [ ] A new developer can follow the README from a fresh clone.
- [ ] The sample scenario generates a visible optimized route.
- [ ] Tests pass without contacting external services.

## Milestone 10: V1 cleanup and release

**Goal:** Produce a stable and presentable first release.

- [ ] Remove dead code and remaining placeholders.
- [ ] Add formatting and linting checks.
- [ ] Review naming and error messages.
- [ ] Add several realistic sample scenarios.
- [ ] Document known limitations.
- [ ] Tag the first release.

**Definition of done:**

- [ ] Tests, formatting, and linting pass.
- [ ] V1 has no database or FastAPI dependency.
- [ ] The README accurately describes the application.
- [ ] The repository is ready for a `v1.0.0` release.

## Recommended sequence

Complete milestones 1 through 5 first to establish the core routing model.
Milestones 6 through 8 turn it into a useful product. Milestones 9 and 10 make
the project reproducible and ready to release.
