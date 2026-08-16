from typing import Self

from pydantic import BaseModel, model_validator, ConfigDict

from routeforger.domain.courier import Courier
from routeforger.domain.package import Package


class Scenario(BaseModel):
    model_config = ConfigDict(extra='forbid')

    packages: list[Package]
    couriers: list[Courier]

    @model_validator(mode="after")
    def validate_lists_and_ids(self) -> Self:
        """Validate scenario contents, IDs, and deadlines."""
        if not self.packages:
            raise ValueError("packages list cannot be empty")

        if len(self.couriers) != 1:
            raise ValueError("a scenario must contain exactly one courier")

        package_ids = [package.id for package in self.packages]
        if len(package_ids) != len(set(package_ids)):
            raise ValueError("package IDs must be unique")

        courier_ids = [courier.id for courier in self.couriers]
        if len(courier_ids) != len(set(courier_ids)):
            raise ValueError("courier IDs must be unique")

        start_time = min([courier.start_time for courier in self.couriers])
        for package in self.packages:
            if package.deadline <= start_time:
                raise ValueError("package deadline before couriers start time")
            
        return self
