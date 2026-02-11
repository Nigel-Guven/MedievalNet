from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from objects.script_enums import Building

@dataclass
class SettlementConfiguration:
    region: str
    level: str
    year_founded: int = 0
    population: int = 0
    plan_set: str = "default_set"
    faction_creator: str = "slave"
    is_castle: bool = False
    buildings: List[Building] = field(default_factory=list)
    