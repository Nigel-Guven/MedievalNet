from dataclasses import dataclass

from objects.settlementconfiguration import SettlementConfiguration

@dataclass
class Region:
        province_name: str
        settlement_name: str
        culture: str
        rebels_type: str
        rgb_value: tuple[int, int, int] 
        features: str
        famine_level: str
        agriculture_level: str
        religions: dict[str, int]
        settlement_positionX: int
        settlement_positionY: int
        settlement_configuration: SettlementConfiguration