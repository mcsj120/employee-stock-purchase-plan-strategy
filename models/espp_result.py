from dataclasses import dataclass

@dataclass
class ESPPResult:
    baseline_value: float = 0.0
    total_value: float = 0.0
    money_contributed: float = 0.0
    roi: float = 0.0
    money_refunded: float = 0.0

    def add(self, other: 'ESPPResult'): 
        self.baseline_value+=other.baseline_value
        self.total_value+=other.total_value
        self.money_contributed+=other.money_contributed
        self.roi+=other.roi
        self.money_refunded+=other.money_refunded
        