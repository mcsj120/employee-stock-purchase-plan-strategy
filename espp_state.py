"""
    Moved to its own file to avoid circular imports
"""
class ESPPState():
    """
        Object to contain the current state of the ESPP run. Helps abstract away a lot of the information that may be needed
        in calculating a espp strategy.
    """

    def __init__(self):
        self.last_contribution = 0
        # Amount contributed to ESPP
        self.dollars_ready_for_purchase = 0
        # Amount contributed to ESPP over both stock plans
        self.total_contributed = 0

        # Shares purchased
        self.shares_purchased = 0
        #Value of the stocks purchased
        self.espp_dollar_value = 0
        self.irs_purchase_value = 0

        # The cost of the stock at the beginning of the offering period
        self.last_grant_price = 0
        self.current_stock_price = 0

        # The contributions and uninvested money for each period
        self.contributions = []
        self.uninvested = []

        # Represents money deliberately not contributed to the ESPP, and the interest gained on that money
        self.money_not_contributed = 0
        self.value_of_money_not_contributed = 0

        self.period = 0
        self.total_periods = 0

        self.money_refunded = 0

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_value_of_money_not_contributed(self, rate_of_return, company_stock_plan):
        self.value_of_money_not_contributed = (
            self.value_of_money_not_contributed * 
            (1 + (rate_of_return / (company_stock_plan.pay_periods_per_offering * company_stock_plan.offering_periods)))
        )

    def update_stock_values_after_purchase(self, shares_purchased_in_period, leftover_cash, stock_price):
        self.shares_purchased += shares_purchased_in_period
        self.espp_dollar_value += shares_purchased_in_period * stock_price
        self.irs_purchase_value += shares_purchased_in_period * self.last_grant_price
        self.money_not_contributed += leftover_cash
        self.value_of_money_not_contributed += leftover_cash
        self.money_refunded += leftover_cash
        self.total_contributed -= leftover_cash
        self.dollars_ready_for_purchase = 0

    def update_contributions_and_uninvested(self, contribution, uninvested_money):
        self.contributions.append(contribution)
        self.uninvested.append(uninvested_money)
        self.money_not_contributed += uninvested_money
        self.value_of_money_not_contributed += uninvested_money
        self.total_contributed += contribution
        self.dollars_ready_for_purchase += contribution