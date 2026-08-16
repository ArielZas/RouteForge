from pydantic import BaseModel, ConfigDict, Field, field_validator


class Courier(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0)
    start_address: str
    start_node: int | None = None
    start_time: int = Field(ge=0, lt=86_400)

    @field_validator("start_address")
    @classmethod
    def validate_start_address(cls, address: str) -> str:
        """Strip and validate the courier's start address."""
        address = address.strip()
        if not address:
            raise ValueError("courier start address cannot be empty")
        return address

    @field_validator("start_node")
    @classmethod
    def validate_start_node_is_unset(cls, node: int | None) -> None:
        """Ensure new couriers have not been geocoded yet."""
        if node is not None:
            raise ValueError("start node must be None when a courier is created")
        return None
