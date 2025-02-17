from datetime import datetime
import typing as t

import numpy as np

from models.company_plan import CompanyStockPlan
from models.company_stock_start_parameters import CompanyStockStartParameters
from espp_scenario_run import ESPPScenarioRun
from models.employee_options import (
    EmployeeOptions, 
    max_all_the_way, 
    max_all_the_way_company_hard_block,
    max_all_the_way_irs_hard_block,
    readjust_halfway
)
from constants import MAX_PRICE_IRS

from sample_parameters.constants_company_plans import cvs_stock_plan
from sample_parameters.constants_company_stock_start_parameters import cvs_stock_params

import strategies
from utils import get_all_functions

def full_run_main():

    prices = generate_scenarios(
        cvs_stock_plan,
        cvs_stock_params
    )
    run_strategies_against_scenario(prices)

def load_file_main(file: str):
    # Example: prices_CVS_20250119_140005.csv
    prices = np.loadtxt(file, delimiter=',')
    run_strategies_against_scenario(prices)
        
def run_strategies_against_scenario(prices: np.ndarray):
    all_functions = get_all_functions(strategies)
    print("Functions in strategies.py:", all_functions)
    for func in all_functions:
        total_value = 0
        total_roi = 0
        print(f'Running scenario {func.__name__}')
        for price in prices:
            end_value, roi = ESPPScenarioRun(
                price,
                EmployeeOptions(
                    cvs_stock_plan,
                    947.51,
                    0,
                    0.05,
                    0.15
                ),
                func
            ).run()
            total_value += end_value
            total_roi += roi
        print(f'The average value for scenario {func.__name__} is {total_value/len(prices)}')
        print(f'The average roi for the espp plan for scenario {func.__name__} is {total_roi/len(prices)}')


def generate_scenarios(
        company_stock_plan: CompanyStockPlan,
        company_stock_start_parameters: CompanyStockStartParameters,
        simulations=1000
    ):
    time_frame = 1
    steps = int(company_stock_plan.pay_periods_per_offering * company_stock_plan.offering_periods)

    # Change in time over each iteration
    dt = time_frame / steps

    prices = np.zeros((simulations, steps + 1))
    prices[:, 0] = company_stock_start_parameters.initial_price

    for t in range(1, steps + 1):
        z = np.random.standard_normal(simulations)  # random variable
        # Monte Carlo formula: S(t+1) = S(t) * exp((r - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * z)
        prices[:, t] = (
            prices[:, t - 1] *
            np.exp(
                (company_stock_start_parameters.expected_rate_of_return - 0.5 * company_stock_start_parameters.volatility**2) * dt + 
                company_stock_start_parameters.volatility * np.sqrt(dt) * z
            )
        )

    np.savetxt(f'prices_{company_stock_plan.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', prices, delimiter=',')
    return prices

def old_test():
    current_plan: CompanyStockPlan = cvs_stock_plan
    scenario_1 = {
        'grant_date_share_price': 80.85,
        'purchase_value_share_price': 59.06,
        'stocks_purchased': 205.53
    }

    scenario_2 = {
        'grant_date_share_price': 80.85,
        'purchase_value_share_price': 100.0,
        'stocks_purchased': 120.04
    }


    s=scenario_1

    grant_date_share_price_1 = s['grant_date_share_price']
    purchase_value_share_price_1 = s['purchase_value_share_price']
    stocks_purchased_1 = s['stocks_purchased']
    period_1_total_contributions = stocks_purchased_1 * purchase_value_share_price_1*(current_plan.discount_rate)
    period_1_paycheck_contributions = period_1_total_contributions/current_plan.pay_periods_per_offering
    period_1_irs_contributions = stocks_purchased_1 * grant_date_share_price_1


    grant_date_share_price_2 = 0
    purchase_value_share_price_2 = 0
    stocks_purchased_2 = 0


    period_2_irs_contributions = MAX_PRICE_IRS - period_1_irs_contributions
    period_2_max_irs_paycheck_contributions = period_2_irs_contributions/current_plan.pay_periods_per_offering

    period_2_total_contributions = (current_plan.max_pay_in - (period_1_total_contributions))
    period_2_max_paycheck_contributions = period_2_total_contributions*current_plan.discount_rate/current_plan.pay_periods_per_offering

    print(f'period_1_paycheck_contributions {period_1_paycheck_contributions}')
    print(f'period_1_irs_contributions {period_1_irs_contributions}')
    print(f'period_1_total_contributions {period_1_total_contributions}')
    print()
    print(f'period_2_irs_contributions {period_2_irs_contributions}')
    print(f'period_2_max_irs_paycheck_contributions {period_2_max_irs_paycheck_contributions}')
    print(f'period_2_total_contributions {period_2_total_contributions}')
    print(f'period_2_max_paycheck_contributions {period_2_max_paycheck_contributions}')

def calculate_maximum_contribution_in_last_period(
    current_irs_contributions: float,
    current_total_contributions: float,
    company_stock_plan: CompanyStockPlan
):
    """
        Given one remaining offering period, calculate the maximum amount of money that can be contributed
        in the last offering period, at a total level and a paycheck level
    """
    max_irs_contributions = MAX_PRICE_IRS - current_irs_contributions
    max_total_contributions = company_stock_plan.max_pay_in - current_total_contributions

    limiting_factor = ''
    
    if max_irs_contributions < max_total_contributions:
        paycheck_contributions = max_irs_contributions/company_stock_plan.pay_periods_per_offering
        limiting_factor = 'IRS'
    elif max_irs_contributions > max_total_contributions:
        paycheck_contributions = max_total_contributions*company_stock_plan.discount_rate/company_stock_plan.pay_periods_per_offering
        limiting_factor = 'Company'
    else:
        limiting_factor = 'equal'
        paycheck_contributions = max_irs_contributions/company_stock_plan.pay_periods_per_offering

    print(f"The limiting factor is {limiting_factor}, and you can contribute {paycheck_contributions} per paycheck, for a total contribution of {max_total_contributions}")


if __name__ == '__main__':
    full_run_main()