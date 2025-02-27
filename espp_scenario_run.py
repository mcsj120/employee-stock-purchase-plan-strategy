import math
import typing as t

import numpy as np

from constants import MAX_PRICE_IRS
from espp_state import ESPPState
from models.employee_options import EmployeeOptions
from models.espp_result import ESPPResult

class ESPPScenarioRun():
    def __init__(
        self,
        scenario: np.ndarray,
        strategy: EmployeeOptions,
        step_function: t.Callable[[EmployeeOptions, ESPPState], t.Tuple[float, float]]
    ):
        self.scenario = scenario
        self.strategy = strategy
        self.current_step = 0
        self.step_function = step_function
        self.state = ESPPState()

    
    def run(self):
        """
            Run the ESPP scenario with the given strategy and state

            Returns the average value and the average roi
        """

        self.state.total_periods = len(self.scenario)
        
        for period, stock_price in enumerate(self.scenario):

            self.state.period = period
            self.state.current_stock_price = stock_price

            # Compound the money that is not invested 
            self.state.update_value_of_money_not_contributed(self.strategy.rate_of_return, self.strategy.company_stock_plan)

            # If the period is the end of an offering period, purchase shares
            if period != 0 and period % self.strategy.company_stock_plan.pay_periods_per_offering == 0 and self.state.dollars_ready_for_purchase != 0:
                # Stock purchase price = floor of current price, price at the beginning of the offering period
                stock_purchase_price = (
                    min(
                        stock_price,
                        self.state.last_grant_price
                    ) * self.strategy.company_stock_plan.discount_rate
                )

                # How many shares can you purchase with no limit
                shares_purchased_in_period = self.state.dollars_ready_for_purchase / stock_purchase_price
                leftover_cash = 0
                cap_hit_irs = False
                cap_hit_company = False
                # How many shares can you purchase with IRS limits
                if (self.state.irs_purchase_value + (self.state.last_grant_price * shares_purchased_in_period)) > MAX_PRICE_IRS:
                    shares_purchased_in_period_irs = (MAX_PRICE_IRS - self.state.irs_purchase_value) / self.state.last_grant_price
                    leftover_cash_irs = self.state.dollars_ready_for_purchase - (shares_purchased_in_period_irs * stock_purchase_price)
                    cap_hit_irs = True
                # How many shares can you purchase with Stock limits
                if (self.state.espp_dollar_value + (stock_purchase_price * shares_purchased_in_period)) > (MAX_PRICE_IRS * self.strategy.company_stock_plan.discount_rate):
                    shares_purchased_in_period_company = ((MAX_PRICE_IRS * self.strategy.company_stock_plan.discount_rate) - self.state.espp_dollar_value) / self.state.last_grant_price
                    leftover_cash_company = self.state.dollars_ready_for_purchase - (shares_purchased_in_period_company * stock_purchase_price)
                    cap_hit_company = True

                # If a cap hit, choose the smaller of the caps to apply.
                if cap_hit_irs and cap_hit_company:
                    if shares_purchased_in_period_irs < shares_purchased_in_period_company:
                        shares_purchased_in_period = shares_purchased_in_period_irs
                        leftover_cash = leftover_cash_irs
                    else:
                        shares_purchased_in_period = shares_purchased_in_period_company
                        leftover_cash = leftover_cash_company
                elif cap_hit_irs:
                    shares_purchased_in_period = shares_purchased_in_period_irs
                    leftover_cash = leftover_cash_irs
                elif cap_hit_company:
                    shares_purchased_in_period = shares_purchased_in_period_company
                    leftover_cash = leftover_cash_company

                self.state.update_stock_values_after_purchase(shares_purchased_in_period, leftover_cash, stock_price)
                    
            # break out of loop once the last purchase has occured
            if period == len(self.scenario) - 1:
                break

            # Reset the IRS grant price at the beginning of each offering period, after shares are purchased
            if period % self.strategy.company_stock_plan.pay_periods_per_offering == 0:
                self.state.last_grant_price = stock_price

            contribution, uninvested_money = self.step_function(
                self.strategy,
                self.state
            )

            self.state.update_contributions_and_uninvested(contribution, uninvested_money)

        return ESPPResult(
            baseline_value=self.strategy.max_contribution * self.state.total_periods,
            money_contributed=self.state.total_contributed,
            money_refunded=self.state.money_refunded,
            total_value=self.state.espp_dollar_value + self.state.value_of_money_not_contributed,
            roi=((1 - self.strategy.capital_gains_tax_rate) * (self.state.espp_dollar_value - self.state.total_contributed)) / self.state.total_contributed
        )

        # print("money_not_contributed", money_not_contributed)
        # print("value_of_money_not_contributed", value_of_money_not_contributed)
        # print("total_contributed", total_contributed)
        # print("espp_value", espp_dollar_value)
        # print("total value", espp_dollar_value + value_of_money_not_contributed)

