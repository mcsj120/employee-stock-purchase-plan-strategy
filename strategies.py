
from constants import MAX_PRICE_IRS
from espp_state import ESPPState
from models.employee_options import EmployeeOptions

def max_all_the_way(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible in each offering period, without regard for company limits
            or IRS limits.
    """
    return (strategy.max_contribution, 0)

def max_all_the_way_company_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible in each offering period, but the company limits the amount
        you can contribute once the cap hits.
        The hard block doesn't let you contribute over the max pay in.
    """

    contribution = strategy.max_contribution
    uninvested = 0
    if state.total_contributed + contribution > strategy.company_stock_plan.max_pay_in:
        contribution = strategy.company_stock_plan.max_pay_in - state.total_contributed
        uninvested = strategy.max_contribution - contribution

    return (contribution, uninvested)

def max_all_the_way_irs_hard_block(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible in each offering period, but the irs limits the amount
        you can contribute once the cap hits.
        The soft block lets you contribute over the max pay in for that pay period, and returns you the money when shares are purchased.
    """

    contribution = strategy.max_contribution
    uninvested = 0
    if state.irs_purchase_value + state.dollars_ready_for_purchase + contribution > MAX_PRICE_IRS:
        contribution = MAX_PRICE_IRS - state.dollars_ready_for_purchase - state.irs_purchase_value
        uninvested = strategy.max_contribution - contribution

    return (contribution, uninvested)

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
    uninvested = strategy.max_contribution - contribution

    return (contribution, uninvested)


def readjust_halfway(strategy: EmployeeOptions, state: ESPPState):
    """
        This plan is to contribute the maximum amount possible for the first offering period, but then readjust the contribution
        to the amount the IRS allows for the second offering period.

    """
    uninvested = 0
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
    ):
        contribution = 0
        uninvested = strategy.max_contribution
    else:
        contribution = state.contributions[-1]
        uninvested = state.uninvested[-1]

    return (contribution, uninvested)