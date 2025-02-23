from constants import MAX_PRICE_IRS

class CompanyStockPlan:
    def __init__(
        self,
        name: str,
        discount_rate: float,
        offering_periods: float,
        pay_periods_per_offering: float,
        cost_to_sell: float
    ):
        """
            discount_rate: The discount rate at which the stock is purchased
            offering_periods: The number of offering periods in a year
            pay_periods_per_offering: The number of pay periods in an offering period
            cost_to_sell: The cost to sell the stock

            may_pay_in: The maximum amount of money an employee can put into the ESPP
        """
        self.name = name
        self.discount_rate = discount_rate
        self.offering_periods = offering_periods
        self.pay_periods_per_offering = pay_periods_per_offering
        self.max_pay_in = MAX_PRICE_IRS * self.discount_rate
        self.cost_to_sell = cost_to_sell

