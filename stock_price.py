from datetime import datetime
import typing as t
import io

import numpy as np
import cairo
import math

from charts import save_roi_distribution_chart
from models.company_plan import CompanyStockPlan
from models.company_stock_start_parameters import CompanyStockStartParameters
from espp_scenario_run import ESPPScenarioRun
from models.employee_options import (
    EmployeeOptions
)

from models.espp_result import ESPPResult
import strategies


def run_strategies_against_scenarios(
    prices: np.ndarray,
    employee_options: EmployeeOptions,
    functions: t.Optional[t.List[t.Dict[str, t.Any]]] = None
):
    if functions is None:
        functions = strategies.get_all_strategies()
    for func in functions:
        function_name: str = func["name"] # type: ignore
        print(f'\nRunning scenario {function_name}\n')
        running_ESPPResult = ESPPResult()
        for price in prices:
            espp_state = ESPPScenarioRun(
                price,
                employee_options,
                func["strategy"] # type: ignore
            ).run()
            running_ESPPResult.add(espp_state)

        func['pic_bytes'] = save_roi_distribution_chart(
            function_name,
            running_ESPPResult.roi,
            employee_options
        )
        func['espp_result'] = running_ESPPResult
    return functions

def run_scenarios_against_strategies(
    prices: np.ndarray,
    employee_options: EmployeeOptions,
    functions: t.Optional[t.List[t.Dict[str, t.Any]]] = None
):
    functions = strategies.get_all_strategies()
    for func in functions:
        func["espp_result"] = ESPPResult() 
    for price in prices:
        for func in functions:
            espp_state = ESPPScenarioRun(
                price,
                employee_options,
                func["strategy"]
            ).run()
            func["espp_result"].add(espp_state)
    
    high_mean = 0
    high_std = 0
    for func in functions:
        if np.mean(func["espp_result"].roi) > high_mean:
            high_mean = np.mean(func["espp_result"].roi)
            high_std = np.std(func["espp_result"].roi)

    for func in functions:
        func['pic_bytes'] = save_roi_distribution_chart(func["name"], func["espp_result"].roi, employee_options, top_value=round(high_mean + (high_std * 3), 2))
    return functions


def generate_scenarios(
    company_stock_plan: CompanyStockPlan,
    company_stock_start_parameters: CompanyStockStartParameters,
    file_name: t.Optional[str] = None,
    simulations=1000
):
    time_frame = 1
    steps = int(company_stock_plan.pay_periods_per_offering * company_stock_plan.offering_periods)

    # Change in time over each iteration
    dt = time_frame / steps

    prices = np.zeros((simulations, steps + 1))
    prices[:, 0] = company_stock_start_parameters.initial_price

    for t in range(1, steps + 1):
        # potential to enhance: https://medium.com/@polanitzer/forward-looking-monte-carlo-simulation-predict-the-future-value-of-equity-using-the-lognormal-f54320f9c230
        # "This process produces log-normally distributed prices, because it exponentiates normally distributed returns."
        z = np.random.normal(simulations)  # random variable
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