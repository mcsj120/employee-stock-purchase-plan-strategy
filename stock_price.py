from datetime import datetime
import uuid

import numpy as np

from models.company_plan import CompanyStockPlan
from models.company_stock_start_parameters import CompanyStockStartParameters
from espp_scenario_run import ESPPScenarioRun
from models.employee_options import (
    EmployeeOptions
)

from models.espp_result import ESPPResult
import strategies
from utils import get_all_functions


def run_strategies_against_scenario(prices: np.ndarray, employee_options: EmployeeOptions):
    all_functions = get_all_functions(strategies)
    print("Functions in strategies.py:", all_functions)
    for func in all_functions:
        running_ESPPResult = ESPPResult()
        print(f'Running scenario {func.__name__}')
        for price in prices:
            espp_state = ESPPScenarioRun(
                price,
                employee_options,
                func
            ).run()
            running_ESPPResult.add(espp_state)
        print(f'The baseline value for scenario {func.__name__} is {running_ESPPResult.baseline_value/len(prices)}')
        print(f'The average total value for the espp plan for scenario {func.__name__} is {running_ESPPResult.total_value/len(prices)}')
        print(f'The average money_contributed for the espp plan for scenario {func.__name__} is {running_ESPPResult.money_contributed/len(prices)}')
        print(f'The average roi for the espp plan for scenario {func.__name__} is {running_ESPPResult.roi/len(prices)}')
        print(f'The average money refunded for the espp plan for scenario {func.__name__} is {running_ESPPResult.money_refunded/len(prices)}')
    return {
        
    }



def generate_scenarios(
    company_stock_plan: CompanyStockPlan,
    company_stock_start_parameters: CompanyStockStartParameters,
    file_name: str = None,
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
    if file_name is None or len(file_name) == 0:
        file_name = f'prices_{company_stock_plan.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    np.savetxt(f'{file_name}.csv', prices, delimiter=',')
    return prices