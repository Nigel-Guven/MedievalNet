from dataclasses import dataclass, field
from decimal import Decimal

@dataclass
class FactionCharacterNames:
    faction: str
    male_names: list[str] = field(default_factory=list)
    surnames: list[str] = field(default_factory=list)
    bynames: list[str] = field(default_factory=list)
    female_names: list[str] = field(default_factory=list)

@dataclass
class Faction:
    faction_name: str
    ai_model: str
    ai_label: str
    denari: int
    kings_purse: int
    settlements: list
    characters: list
    character_records: list
    factionCharacterNames : FactionCharacterNames
    factionRelations : dict[Decimal, list] = field(default_factory=dict)
    enemies: list = field(default_factory=list)
        

    