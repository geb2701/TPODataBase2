from __future__ import annotations  # para referencias tardías
from pydantic import BaseModel, Field
from datetime import date, datetime

class Historial(BaseModel):
    fecha: datetime = Field(default_factory=datetime.combine(date.today(), datetime.min.time()))
    mensage: str
