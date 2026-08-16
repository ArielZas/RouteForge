import json
from pathlib import Path
from typing import Any

from routeforger.domain.scenario import Scenario
from routeforger.time_utils import time_string_to_seconds


def load_scenario(json_file: str | Path) -> Scenario:
    """Load and validate a scenario from JSON."""
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

        for courier in data["couriers"]:
            courier["start_time"] = time_string_to_seconds(courier["start_time"])

        for package in data["packages"]:
            package["deadline"] = time_string_to_seconds(package["deadline"])

        return Scenario.model_validate(data)
