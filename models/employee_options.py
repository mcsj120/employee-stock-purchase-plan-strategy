from models.company_plan import CompanyStockPlan
from models.company_stock_start_parameters import CompanyStockStartParameters

class EmployeeOptions:
    def __init__(
        self,
        company_stock_plan: CompanyStockPlan,
        company_stock_parameters: CompanyStockStartParameters,
        max_contribution,
        steps_to_zero: int,
        liquidity_preference_rate: float,
        capital_gains_tax_rate: float,
        default_to_max_allowed=False
    ):
        """
            rate_of_return represents the expected rate of return for uninvested money

            Max contribution represents the starting contribution that a person may make.

            capital_gains_tax_rate is the tax rate for capital gains. For ease of use,
            it is not applied to the liquidity preference rate.
            

            Parameters to add:
                Give the ability to increase contribution in an offering period
                Give the ability to pick dollar amounts to decrease, instead of percentage
                Give the ability to use volatility/expected return to make decisions.
                    Keeping parameters light, so not adding company_stock_start_parameters yet
        """
        self.company_stock_plan = company_stock_plan
        self.company_stock_parameters = company_stock_parameters
        self.max_contribution = max_contribution
        self.steps_to_zero = steps_to_zero
        self.rate_of_return = liquidity_preference_rate
        self.capital_gains_tax_rate = capital_gains_tax_rate

