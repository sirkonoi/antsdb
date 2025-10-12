from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class SpeciesCreate(BaseModel):
    scientific_name: str
    genus: Optional[str] = "Unknown"
    species: Optional[str] = "Unknown"
    subspecies: Optional[str] = "Unknown"
    family: Optional[str] = "Unknown"
    subfamily: Optional[str] = "Unknown"
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SpeciesRevisionCreate(BaseModel):
    author_id: int
    content: dict
    approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
