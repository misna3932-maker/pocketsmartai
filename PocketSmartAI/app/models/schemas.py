from typing import Optional
from pydantic import BaseModel, Field, field_validator

class HomePlannerInput(BaseModel):
    total_budget: float = Field(gt=0)
    lights: int = Field(default=0, ge=0)
    ceiling_fans: int = Field(default=0, ge=0)
    furniture: int = Field(default=0, ge=0)
    dining_tables: int = Field(default=0, ge=0)
    rooms: list[str] = Field(default_factory=list)
    notes: str = ""

class PartyPlannerInput(BaseModel):
    total_budget: float = Field(gt=0)
    guests: int = Field(gt=0)
    party_type: str = "Birthday"
    venue_type: str = "Home"
    needs: list[str] = Field(default_factory=list)
    notes: str = ""

class JewelryPlannerInput(BaseModel):
    total_budget: float = Field(gt=0)
    occasion: str = "Birthday"
    style_preferences: str = ""
    outfit_image: Optional[str] = None
