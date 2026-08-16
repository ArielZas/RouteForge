// Create the Leaflet map and center it on the Tel Aviv area before a route is
// calculated. Once results arrive, the map automatically zooms to the route.
const map = L.map("map").setView([32.0853, 34.7818], 12);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

// Cache frequently used DOM elements so they do not have to be queried every
// time the user adds a package or submits the form.
const form = document.querySelector("#route-form");
const packageList = document.querySelector("#package-list");
const packageTemplate = document.querySelector("#package-template");
const errorBox = document.querySelector("#error");
const submitButton = document.querySelector("#submit");

// These hold the currently displayed Leaflet layers. Keeping references lets
// us remove an old result before drawing a newly calculated route.
let routeLayer;
let markerLayer;

/**
 * Convert the value of an HTML time input (for example, "08:30") into the
 * number of seconds since midnight expected by the backend API.
 */
function timeToSeconds(value) {
  const [hours, minutes] = value.split(":").map(Number);
  return hours * 3600 + minutes * 60;
}

/**
 * Convert seconds since midnight back into a human-readable 24-hour time.
 * Modulo keeps times valid if a long route happens to continue past midnight.
 */
function formatClock(value) {
  if (value == null) {
    return "Not delivered";
  }

  const secondsInDay = 86400;
  const normalizedSeconds = Math.round(value) % secondsInDay;
  const hours = Math.floor(normalizedSeconds / 3600);
  const minutes = Math.floor((normalizedSeconds % 3600) / 60);

  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

/** Format a duration supplied in seconds as minutes, or hours and minutes. */
function formatDuration(value) {
  const totalMinutes = Math.round(value / 60);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  return hours ? `${hours}h ${minutes}m` : `${minutes} min`;
}

/**
 * Keep package headings and the package counter synchronized with the cards
 * currently in the form. A single remaining package cannot be removed because
 * the scenario must contain at least one package.
 */
function renumberPackages() {
  const packageCards = [...packageList.children];

  packageCards.forEach((card, index) => {
    card.querySelector("strong").textContent = `Package ${index + 1}`;
    card.querySelector(".remove").hidden = packageCards.length === 1;
  });

  const packageWord = packageCards.length === 1 ? "package" : "packages";
  document.querySelector("#package-count").textContent =
    `${packageCards.length} ${packageWord}`;
}

/**
 * Add a package card to the form. Optional data is used to prefill the card,
 * which is how the richer default test scenario is loaded at startup.
 */
function addPackage(data = {}) {
  const fragment = packageTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".package");

  card.querySelector('[name="source"]').value = data.source || "";
  card.querySelector('[name="destination"]').value = data.destination || "";
  card.querySelector('[name="deadline"]').value = data.deadline || "";

  card.querySelector(".remove").addEventListener("click", () => {
    card.remove();
    renumberPackages();
  });

  packageList.append(fragment);
  renumberPackages();
}

/**
 * Read the current form and construct the exact request body accepted by the
 * route API. Package IDs are regenerated from the visible card order.
 */
function buildScenario() {
  const packageCards = [...packageList.children];

  return {
    couriers: [
      {
        id: 1,
        start_address: document.querySelector("#start-address").value.trim(),
        start_time: timeToSeconds(document.querySelector("#start-time").value),
      },
    ],
    packages: packageCards.map((card, index) => ({
      id: index + 1,
      source_address: card.querySelector('[name="source"]').value.trim(),
      destination_address: card
        .querySelector('[name="destination"]')
        .value.trim(),
      deadline: timeToSeconds(
        card.querySelector('[name="deadline"]').value,
      ),
    })),
  };
}

/**
 * Attach a tooltip that opens only while the pointer is over a route marker.
 * A custom class can distinguish the courier start from package stops.
 */
function addHoverTooltip(marker, label, className = "stop-label") {
  marker.bindTooltip(label, {
    direction: "top",
    offset: [0, -8],
    className,
  });

  marker.on("mouseover", () => marker.openTooltip());
  marker.on("mouseout", () => marker.closeTooltip());

  return marker;
}

/** Draw the calculated road route and its pickup/delivery markers on the map. */
function plotRoute(data) {
  // Remove the previous calculation so repeated submissions do not overlap.
  if (routeLayer) {
    routeLayer.remove();
  }

  if (markerLayer) {
    markerLayer.remove();
  }

  const routePoints = data.route.map((point) => [
    point.latitude,
    point.longitude,
  ]);

  routeLayer = L.polyline(routePoints, {
    color: "#176b52",
    weight: 6,
    opacity: 0.95,
  }).addTo(map);

  markerLayer = L.layerGroup().addTo(map);

  // The first route coordinate represents the courier's starting position.
  if (routePoints.length) {
    const startMarker = L.circleMarker(routePoints[0], {
      radius: 9,
      color: "white",
      weight: 3,
      fillColor: "#17201d",
      fillOpacity: 1,
    });

    addHoverTooltip(
      startMarker,
      "Courier start",
      "stop-label start-label",
    ).addTo(markerLayer);
  }

  // A stop may contain multiple events when pickup and delivery locations
  // coincide, so its label and popup are assembled from every stop event.
  data.stops.forEach((stop) => {
    const labels = stop.events.map((event) => {
      const action = event.type === "pickup" ? "Pickup" : "Delivery";
      return `${action} #${event.package_id}`;
    });

    const marker = L.circleMarker([stop.latitude, stop.longitude], {
      radius: 8,
      color: "white",
      weight: 3,
      fillColor: "#176b52",
      fillOpacity: 1,
    }).bindPopup(
      `${labels.join("<br>")}<br>Arrival: ${formatClock(stop.arrival_time)}`,
    );

    addHoverTooltip(marker, labels.join(" · ")).addTo(markerLayer);
  });

  // Show the complete result when possible, while still handling a route with
  // only one coordinate gracefully.
  if (routePoints.length > 1) {
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
  } else if (routePoints.length === 1) {
    map.setView(routePoints[0], 16);
  }
}

/** Populate the summary and detailed result panels from a successful response. */
function displayResults(data) {
  document.querySelector("#distance").textContent =
    `${(data.total_distance / 1000).toFixed(1)} km`;
  document.querySelector("#duration").textContent = formatDuration(
    data.total_duration,
  );
  document.querySelector("#stops").textContent = data.stops.length;

  document.querySelector("#summary").hidden = false;
  document.querySelector("#details").hidden = false;

  document.querySelector("#stop-list").innerHTML = data.stops
    .map((stop) => {
      const events = stop.events
        .map((event) => `${event.type} package ${event.package_id}`)
        .join(" + ");

      return `<li>${events} — ${formatClock(stop.arrival_time)}</li>`;
    })
    .join("");

  document.querySelector("#package-results").innerHTML = data.packages
    .map((packageResult) => {
      const status = packageResult.deadline_met ? "On time" : "Late";
      const statusClass = packageResult.deadline_met ? "on-time" : "late";

      return `
        <div class="result-package">
          <b>Package ${packageResult.id}</b>
          <span class="${statusClass}">
            ${status} · ${formatClock(packageResult.delivery_time)}
          </span>
        </div>
      `;
    })
    .join("");

  plotRoute(data);
}

/**
 * Parse an HTTP response as JSON when possible. Returning plain text as a
 * fallback allows useful server error messages to reach the user.
 */
async function parseResponse(response) {
  const responseText = await response.text();

  try {
    return JSON.parse(responseText);
  } catch {
    return responseText;
  }
}

/** Remove address errors left by a previous route request. */
function clearAddressErrors() {
  form.querySelectorAll(".address-field-error").forEach((message) => {
    message.remove();
  });

  form.querySelectorAll('input[aria-invalid="true"]').forEach((input) => {
    input.removeAttribute("aria-invalid");
    input.classList.remove("input-error");
  });
}

/**
 * Display an API address error beneath the input containing that address.
 * Returns false if the corresponding field no longer exists in the form.
 */
function showAddressError(address, message) {
  const addressInputs = [
    document.querySelector("#start-address"),
    ...form.querySelectorAll('[name="source"], [name="destination"]'),
  ];
  const normalizedAddress = address.trim().toLocaleLowerCase();
  const input = addressInputs.find(
    (candidate) =>
      candidate.value.trim().toLocaleLowerCase() === normalizedAddress,
  );

  if (!input) {
    return false;
  }

  input.setAttribute("aria-invalid", "true");
  input.classList.add("input-error");

  const fieldMessage = document.createElement("span");
  fieldMessage.className = "address-field-error";
  fieldMessage.textContent = message;
  input.insertAdjacentElement("afterend", fieldMessage);
  input.focus();

  return true;
}

// Calculate a route through the backend API instead of allowing the browser to
// perform the form's normal page-navigation submission.
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  errorBox.hidden = true;
  clearAddressErrors();
  submitButton.disabled = true;
  submitButton.textContent = "Forging route…";

  try {
    const response = await fetch("/api/routes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildScenario()),
    });

    const data = await parseResponse(response);

    if (!response.ok) {
      const addressError = data.detail?.code === "address_not_found";

      if (addressError) {
        const displayedOnField = showAddressError(
          data.detail.address,
          `Address not found: ${data.detail.address}`,
        );

        if (displayedOnField) {
          return;
        }
      }

      const validationMessage = data.detail
        ?.map?.((error) => error.msg)
        .join(" · ");
      const errorMessage =
        typeof data === "string"
          ? data
          : validationMessage ||
            data.detail?.message ||
            data.detail ||
            "Route calculation failed";

      throw new Error(
        typeof errorMessage === "string"
          ? errorMessage
          : "Route calculation failed",
      );
    }

    displayResults(data);
  } catch (error) {
    errorBox.textContent = error.message || "Could not reach the API";
    errorBox.hidden = false;
  } finally {
    // Always restore the button, whether the request succeeded or failed.
    submitButton.disabled = false;
    submitButton.textContent = "Forge my route";
  }
});

// Remove a field-specific server error as soon as the user edits that field.
form.addEventListener("input", (event) => {
  const input = event.target;

  if (!(input instanceof HTMLInputElement) || !input.matches(".input-error")) {
    return;
  }

  input.removeAttribute("aria-invalid");
  input.classList.remove("input-error");
  input.parentElement.querySelector(".address-field-error")?.remove();
});

document.querySelector("#add-package").addEventListener("click", () => {
  addPackage();
});

// Load five packages by default, producing 10 pickup/delivery points spread
// across the Tel Aviv District for a more meaningful optimization scenario.
const defaultPackages = [
  {
    source: "Dizengoff Center, Tel Aviv",
    destination: "Ibn Gabirol 49, Tel aviv",
    deadline: "08:30",
  },
  {
    source: "Wolfson Medical Center, Holon",
    destination: "Habima Theatre, Tel Aviv",
    deadline: "09:15",
  },
  {
    source: "Bialik 20, Ramat Gan",
    destination: "Givatayim Mall, Givatayim",
    deadline: "10:00",
  },
  {
    source: "Ayalon Mall, Ramat Gan",
    destination: "Jabotinsky 35, Ramat Gan",
    deadline: "10:45",
  },
  {
    source: "Kiryat Ono Mall, Kiryat Ono",
    destination: "Rabbi Akiva 72, Bnei Brak",
    deadline: "11:30",
  },
  {
    source: "Sokolov 14, Herzliya",
    destination: "Ibn Gabirol 49, Tel Aviv",
    deadline: "13:15"
  },
  {
    source: "Sokolov 14, Herzliya",
    destination: "Ibn Gabirol 49, Tel Aviv",
    deadline: "13:15"
  },
  {
    source: "Balfour 42, Bat Yam",
    destination: "Bialik 18, Ramat Gan",
    deadline: "14:45"
  },
  {
    source: "Ben Yehuda 122, Tel Aviv",
    destination: "Rabbi Akiva 72, Bnei Brak",
    deadline: "15:30"
  },
  {
    source: "Jabotinsky 35, Ramat Gan",
    destination: "HaNadiv 8, Herzliya",
    deadline: "16:20"
  },
  {
    source: "Rabbi Akiva 72, Bnei Brak",
    destination: "HaRav Maimon 8, Bat Yam",
    deadline: "17:00"
  }
];

defaultPackages.forEach(addPackage);

// The health check provides immediate feedback when the page is open but the
// backend server is unavailable.
fetch("/api/health")
  .then((response) => {
    if (!response.ok) {
      throw new Error("Health check failed");
    }

    const apiStatus = document.querySelector("#api-status");
    apiStatus.textContent = "API connected";
    apiStatus.className = "online";
  })
  .catch(() => {
    const apiStatus = document.querySelector("#api-status");
    apiStatus.textContent = "API offline";
    apiStatus.className = "offline";
  });
