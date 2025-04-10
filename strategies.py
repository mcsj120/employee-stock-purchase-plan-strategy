import math

from scipy.stats import norm

from constants import MAX_PRICE_IRS
from models.espp_state import ESPPState
from models.employee_options import EmployeeOptions

def get_all_strategies():
    return [
        {
            "name": "No contribution to ESPP",
            "strategy": no_contribution,
            "description": "This plan doesn't contribute any money to the ESPP."
        },
        {
            "name": "Max contribution to ESPP with company blocking overpayment",
            "strategy": max_all_the_way_company_hard_block,
            "description": "Contributes max possible each period; company limits contributions once cap hits."
        },
        {
            "name": "Max contribution to ESPP with IRS blocking overpayment",
            "strategy": max_all_the_way_irs_hard_block,
            "description": "Contributes max possible each period; IRS limits contributions once cap hits."
        },
        {
            "name": "Max contribution to ESPP with company and IRS blocking overpayment",
            "strategy": max_both_hard_block,
            "description": "Contributes max possible each period; company and IRS limit contributions once cap hits."
        },
        {
            "name": "Proportioned max contribution to ESPP with company blocking overpayment",
            "strategy": proportioned_max_all_the_way_company_hard_block,
            "description": "Contributes evenly each period to reduce overpayment risk; company limits contributions."
        },
        {
            "name": "Proportioned max contribution to ESPP with company and IRS blocking overpayment",
            "strategy": proportioned_max_both_hard_block,
            "description": "Contributes evenly each period to reduce overpayment risk; company and IRS limit contributions."
        },
        {
            "name": "Reduce IRS overpayment risk",
            "strategy": reduce_irs_over_risk,
            "description": "Averages contributions per period per IRS rules; stops when company limit is hit."
        },
        {
            "name": "Readjust halfway through the offering period",
            "strategy": readjust_halfway,
            "description": "Contributes max first 3 periods; readjusts if stock price drops by 15% halfway through."
        },
        {
            "name": "Maximize for large periods",
            "strategy": maximize_for_large_periods,
            "description": "Implements a strategy that attempts to maximize contributions in high performing periods."
        }
    ]

def get_core_strategies():
    return [
        {
            "name": "No contribution to ESPP",
            "strategy": no_contribution,
            "description": "This plan doesn't contribute any money to the ESPP."
        },
        {
            "name": "Max contribution to ESPP with company and IRS blocking overpayment",
            "strategy": max_both_hard_block,
            "description": "Contributes max possible each period; company and IRS limit contributions once cap hits."
        }
    ]

def get_no_lookback_strategies():
    return [
        {
            "name": "No contribution to ESPP",
            "strategy": no_contribution,
            "description": "This plan doesn't contribute any money to the ESPP."
        },
        {
            "name": "Max contribution to ESPP with company blocking overpayment",
            "strategy": max_all_the_way_company_hard_block,
            "description": "Contributes max possible each period; company limits contributions once cap hits."
        },
        {
            "name": "Max contribution to ESPP with IRS blocking overpayment",
            "strategy": max_all_the_way_irs_hard_block,
            "description": "Contributes max possible each period; IRS limits contributions once cap hits."
        },
        {
            "name": "Max contribution to ESPP with company and IRS blocking overpayment",
            "strategy": max_both_hard_block,
            "description": "Contributes max possible each period; company and IRS limit contributions once cap hits."
        },
        {
            "name": "Proportioned max contribution to ESPP with company blocking overpayment",
            "strategy": proportioned_max_all_the_way_company_hard_block,
            "description": "Contributes evenly each period to reduce overpayment risk; company limits contributions."
        },
        {
            "name": "Proportioned max contribution to ESPP with company and IRS blocking overpayment",
            "strategy": proportioned_max_both_hard_block,
            "description": "Contributes evenly each period to reduce overpayment risk; company and IRS limit contributions."
        },
    ]

def no_contribution(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan doesn't contribute any money to the ESPP.
    """
    return 0

def max_all_the_way_company_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible in each offering period, but the company limits the amount
        you can contribute once the cap hits.
        The hard block doesn't let you contribute over the max pay in.
    """

    contribution = strategy.max_contribution
    if state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = strategy.company_stock_plan.max_pay_in - state.total_contributed

    return contribution

def proportioned_max_all_the_way_company_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible in each offering period, but the company limits the amount
        you can contribute once the cap hits.

        This is different because the max_contribution is reduced to ensure that the company cap is not guaranteed to be hit.

        The hard block doesn't let you contribute over the max pay in.
    """

    contribution = min(strategy.max_contribution, MAX_PRICE_IRS / (strategy.company_stock_plan.offering_periods * strategy.company_stock_plan.pay_periods_per_offering))
    if state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = strategy.company_stock_plan.max_pay_in - state.total_contributed

    return contribution

def max_all_the_way_irs_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible in each offering period, but the irs limits the amount
        you can contribute once the cap hits.
        The soft block lets you contribute over the max pay in for that pay period, and returns you the money when shares are purchased.

        If the stock ends on a price below the last grant price, this function will overcontribute.
        The target price if IRS is the limiting factor is last_grant_price / discount rate. (56 / 0.85)  
    """

    contribution = strategy.max_contribution
    if state.irs_purchased_value + state.dollars_ready_for_purchase + contribution > MAX_PRICE_IRS:
        contribution = MAX_PRICE_IRS - state.dollars_ready_for_purchase - state.irs_purchased_value

    return contribution

def max_both_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan combines the blocking of irs and company
    """

    contribution = strategy.max_contribution
    if state.irs_purchased_value + state.dollars_ready_for_purchase + contribution > MAX_PRICE_IRS:
        contribution = MAX_PRICE_IRS - state.dollars_ready_for_purchase - state.irs_purchased_value
    if contribution != 0 and state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = min(contribution, strategy.company_stock_plan.max_pay_in - state.total_contributed)

    return contribution

def proportioned_max_both_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan combines the blocking of irs and company

        This is different because the max_contribution is reduced to ensure that the company cap is not guaranteed to be hit.
    """

    contribution = min(strategy.max_contribution, MAX_PRICE_IRS / (strategy.company_stock_plan.offering_periods * strategy.company_stock_plan.pay_periods_per_offering))
    if state.irs_purchased_value + state.dollars_ready_for_purchase + contribution > MAX_PRICE_IRS:
        contribution = MAX_PRICE_IRS - state.dollars_ready_for_purchase - state.irs_purchased_value
    if contribution != 0 and state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = min(contribution, strategy.company_stock_plan.max_pay_in - state.total_contributed)

    return contribution

def reduce_irs_over_risk(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is intended to average out the amount you can contribute in each period according to IRS rules, which is 25,000 / the number of offering periods.
        You still may return money from this strategy if the stock price drops, but it will be less than doing a max contribution every period. This is only
        needed if the maximum you can contribute is more than 25,000 per year.
    """
    if state.period % strategy.company_stock_plan.pay_periods_per_offering == 0:
        if strategy.max_contribution < (MAX_PRICE_IRS/(strategy.company_stock_plan.pay_periods_per_offering * strategy.company_stock_plan.offering_periods)):
            contribution = strategy.max_contribution
        else:
            contribution = MAX_PRICE_IRS/(strategy.company_stock_plan.pay_periods_per_offering * strategy.company_stock_plan.offering_periods)
    else:
        contribution = state.contributions[-1]

    # If already over on the company, stops. Rarely hits, still a small net negative compared to other strategies.
    if contribution != 0 and state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = min(contribution, strategy.company_stock_plan.max_pay_in - state.total_contributed)

    return contribution


def readjust_halfway(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible for the first offering period, but then readjust the contribution
        to the amount the IRS allows for the second offering period.
    """
    contribution = 0
    if state.period % strategy.company_stock_plan.pay_periods_per_offering == 0:
        contribution = strategy.max_contribution
    elif (
        # we aren't in the last period
        state.period < strategy.company_stock_plan.pay_periods_per_offering * (strategy.company_stock_plan.offering_periods - 1)
        and
        # we are halfway through the current offering period
        state.period % strategy.company_stock_plan.pay_periods_per_offering == strategy.company_stock_plan.pay_periods_per_offering / strategy.company_stock_plan.offering_periods/ 2
        and 
        # the stock price has dropped by X% (todo: parameterize)
        state.last_grant_price * 0.85 > state.current_stock_price
        #and
        # the plan has been funded to 80% of the IRS limit
        # this didn't yield positive results
        #state.total_contributed > MAX_PRICE_IRS * 0.9
    ):
        contribution = 0
    else:
        contribution = state.contributions[-1]

    if state.irs_purchased_value + state.dollars_ready_for_purchase + contribution > MAX_PRICE_IRS:
        contribution = MAX_PRICE_IRS - state.dollars_ready_for_purchase - state.irs_purchased_value
    if contribution != 0 and state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = min(contribution, strategy.company_stock_plan.max_pay_in - state.total_contributed)

    return contribution

def maximize_for_large_periods(strategy: EmployeeOptions, state: ESPPState):
    """
        After trial and error, the best returns are those that can capture when a stock dramatically rises.
        This is difficult when there are 2 offering periods, because if you contribute too much in the first period,
        you may not have any money left to contribute in the second period.

        The goal of this strategy is invest as much as possible into high performing periods, and if the first period
        is a low performing period, stop contributing as soon as possible.

        This strategy evaluates the stock price each period, and determine how much to contribute based on the probability of the stock price
        being one standard deviation above the mean expected return.

        There are 2 possible prices to contributein the first period:
            1. MIN(max_contribution, MAX_PRICE_IRS * 2 / (pay_periods_per_offering * offering_periods))
                This would put all of the money into the first period if it is an optimal period
            2. MIN(max_contribution, MAX_PRICE_IRS / (pay_periods_per_offering * offering_periods))
                This is a lower tier value, where high returns are possible, but not completely expected.
                This may be lowered after testing
            3. 0, if the return is not expected to be high
                This may be modified to  Price to hit 1/4 contributions in the first period, to adjust for
                wanting to make sure the plan is being maximized

        In order to determine the probability of the stock price being one standard deviation above the mean expected return,
        we use the z-score formula:
        z = (x - μ) / σ
        where x is the current stock price,
        μ is the mean expected return at the given point in time which uses (1+ror)^(# of months remaining in period / 12),
        and σ is the standard deviation aka the volatility at a given point in time which uses volatility * sqrt(# of months remaining in period / 12).

        To decide what level to contribute, we use 2 linear formulas for contribution 1 and contribution 2. 
        The probability of the return being one standard deviation above the mean needs to above the linear formula in order to contribute at that level.
        However, according to current stock plans, contributions cannot increase in an offering period.

        Currently, I am arbitrarily using 
        L1 = 0.32 + 0.63x, where x is the current period number / total periods in offering period.
            This means to contribute at an L1 level, the probability of the return being one standard deviation above the mean needs to be above 0.32 + 0.43 * (current period number / total periods in offering period).
            The last period needs to have a 75% probability of being one standard deviation above the mean to contribute at the L2 level.
        L2 = 0.32 + 0.43x, where x is the current period number / total periods in offering period.
            This means to contribute at an L1 level, the probability of the return being one standard deviation above the mean needs to be above 0.32 + 0.43 * (current period number / total periods in offering period).
            The last period needs to have a 75% probability of being one standard deviation above the mean to contribute at the L2 level.

        In the second period, the goal is to contribute as much as possible, with company blocks and IRS blocks still
        in place.
    """
    contribution = 0

    level_1_contribution = min(strategy.max_contribution, MAX_PRICE_IRS * 2 / (strategy.company_stock_plan.pay_periods_per_offering * strategy.company_stock_plan.offering_periods))
    level_2_contribution = min(strategy.max_contribution, MAX_PRICE_IRS / (strategy.company_stock_plan.pay_periods_per_offering * strategy.company_stock_plan.offering_periods))

    one_std_dev_above = state.last_grant_price + strategy.company_stock_parameters.volatility
    half_std_dev_above = state.last_grant_price + strategy.company_stock_parameters.volatility / 2
    quarter_std_dev_above = state.last_grant_price + strategy.company_stock_parameters.volatility / 4
    
    std_dev_to_use = half_std_dev_above

    if state.period == 0:
        contribution = level_1_contribution
    elif state.period % strategy.company_stock_plan.pay_periods_per_offering == 0:
        contribution = strategy.max_contribution
    # if not in the last period, however, only planned for 2 periods
    elif state.period < strategy.company_stock_plan.pay_periods_per_offering * (strategy.company_stock_plan.offering_periods - 1):
        if state.contributions[-1] in (level_1_contribution, level_2_contribution):
            current_expected_mean = state.current_stock_price * math.pow((1 + strategy.company_stock_parameters.expected_rate_of_return), state.period / 24) 
            current_expected_volatility = state.current_stock_price * strategy.company_stock_parameters.volatility * math.sqrt(state.period / 24)

            normalized_std_dev_goal = (std_dev_to_use - current_expected_mean) / current_expected_volatility

            # Calculate the probability
            probability = 1 - norm.cdf(normalized_std_dev_goal)

            if probability > 0.32 + 0.63 * (state.period / strategy.company_stock_plan.pay_periods_per_offering) and level_1_contribution == state.contributions[-1]:
                contribution = level_1_contribution
            elif probability > 0.32 +  0.43 * (state.period / strategy.company_stock_plan.pay_periods_per_offering) and state.contributions[-1] in (level_1_contribution, level_2_contribution) :
                contribution = level_2_contribution
            else:
                # fill out the remaining period so a max contribution can be done in the second period.
                # Idea: Multiply by (1 - volatility/2) to account for the stock price dropping
                # assumes 1 period
                # 25000 * discount_rate 
                potential_contribution = (
                    (MAX_PRICE_IRS * strategy.company_stock_plan.discount_rate 
                    - sum(state.contributions)
                    - (strategy.max_contribution * strategy.company_stock_plan.pay_periods_per_offering))
                    * 0.9
                ) / (strategy.company_stock_plan.pay_periods_per_offering - state.period)
                potential_contribution = min(potential_contribution, strategy.max_contribution)
                if potential_contribution > 0:
                    contribution = potential_contribution
                else:
                    contribution = 0
        else:
            contribution = state.contributions[-1]
    else:
        contribution = state.contributions[-1]
    
    if state.irs_purchased_value + state.dollars_ready_for_purchase + contribution > MAX_PRICE_IRS:
        contribution = MAX_PRICE_IRS - state.dollars_ready_for_purchase - state.irs_purchased_value
    if contribution != 0 and state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = min(contribution, strategy.company_stock_plan.max_pay_in - state.total_contributed)

    return contribution