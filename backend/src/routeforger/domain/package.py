from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Package(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0)

    source_address: str
    source_node: int | None = None

    destination_address: str
    destination_node: int | None = None

    deadline: int = Field(ge=0, lt=86_400)

    @field_validator("source_address", "destination_address")
    @classmethod
    def validate_address(cls, address: str) -> str:
        """Strip and validate a package address."""
        address = address.strip()
        if not address:
            raise ValueError("package addresses cannot be empty")
        return address

    @field_validator(
        "source_node",
        "destination_node",
    )
    @classmethod
    def validate_nodes_are_unset(
        cls,
        value: int | None,
    ) -> None:
        """Ensure new packages have not been geocoded yet."""
        if value is not None:
            raise ValueError("nodes must be None when a package is created")
        return None

    @model_validator(mode="after")
    def validate_addresses_are_different(self) -> Self:
        """Ensure pickup and delivery addresses differ."""
        if self.source_address.casefold() == self.destination_address.casefold():
            raise ValueError("source and destination addresses must be different")
        return self
