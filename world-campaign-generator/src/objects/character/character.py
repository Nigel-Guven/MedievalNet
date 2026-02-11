from dataclasses import dataclass, field

from objects.script_enums import Gender

@dataclass
class BaseCharacter:
        character_name: str
        role: None
        age: int
        
@dataclass
class MaleCharacter(BaseCharacter):
        gender: str = Gender.MALE
        defined_character: str = "named character"
        positionX: int = 0 
        positionY: int = 0 
        traits: list = field(default_factory=list)
        ancillaries: str = ""
        army_units: list  = field(default_factory=list)
        
@dataclass
class FemaleCharacter(BaseCharacter):
        gender: str = Gender.FEMALE
        alive: str = "alive"