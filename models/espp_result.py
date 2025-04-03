from dataclasses import dataclass, field

@dataclass
class ESPPResult:
    """
    This class is used to store the results of the ESPP plan.

    The _sum variables represents the sum of multiple ESPPResult objects.

    baseline_value represents the sum of money that can be contributed to the ESPP plan.
    total_value represents the total value of the money that can be contributed to the ESPP plan after the plan is over,
        including share purchases and interest earned.
    money_contributed represents the sum of money that was contributed to the ESPP plan.
    roi represents the return on investment of the ESPP plan including the liquidity preference rate and capital gains tax rate.
    money_refunded represents the sum of money that was refunded from the ESPP plan because too much money was contributed.
    """
    baseline_value_sum: float = 0.0
    total_value_sum: float = 0.0
    money_contributed_sum: float = 0.0
    roi_sum: float = 0.0
    money_refunded_sum: float = 0.0

    baseline_value: list[float] = field(default_factory=list)
    total_value: list[float] = field(default_factory=list)
    money_contributed: list[float] = field(default_factory=list)
    roi: list[float] = field(default_factory=list)
    money_refunded: list[float] = field(default_factory=list)
    

    def add(self, other: 'ESPPResult'): 
        self.baseline_value_sum += sum(other.baseline_value)
        self.total_value_sum += sum(other.total_value)
        self.money_contributed_sum += sum(other.money_contributed)
        self.roi_sum += sum(other.roi)
        self.money_refunded_sum += sum(other.money_refunded)

        self.baseline_value.extend(other.baseline_value)
        self.total_value.extend(other.total_value)
        self.money_contributed.extend(other.money_contributed)
        self.roi.extend(other.roi)
        self.money_refunded.extend(other.money_refunded)