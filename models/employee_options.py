from models.company_plan import CompanyStockPlan
from models.company_stock_start_parameters import CompanyStockStartParameters

class EmployeeOptions:
    def __init__(
        self,
        company_stock_plan: CompanyStockPlan,
        company_stock_parameters: CompanyStockStartParameters,
        max_contribution,
        steps_to_zero: int,
        liquidity_preference_rate: float=0,
        capital_gains_tax_rate: float=0,
        ignore_liquidity_preference: bool=False,
        default_to_max_allowed=False
    ):
        """
            rate_of_return represents the expected rate of return for uninvested money

            Max contribution represents the starting contribution that a person may make.

            capital_gains_tax_rate is the tax rate for capital gains. For ease of use,
            it is not applied to the liquidity preference rate.

            ignore_liquidity_preference means calculations should be done not taking liquidity preference into account.
            This means that if you accidentally tie up money in the ESPP, the strategy ROI will not be penalized.
            This can be useful for seeing the true ESPP ROI
            

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
        self.ignore_liquidity_preference = ignore_liquidity_preference
        self.default_to_max_allowed = default_to_max_allowed

