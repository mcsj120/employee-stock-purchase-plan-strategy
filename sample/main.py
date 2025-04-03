import os
import sys

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from constants_company_plans import cvs_stock_plan
from constants_company_stock_start_parameters import cvs_stock_params
from constants_employee_options import cvs_employee_options


from stock_price import generate_scenarios, run_strategies_against_scenarios

def sample_full_run_main():
    price_sets = generate_scenarios(
        cvs_stock_plan,
        cvs_stock_params
    )
    run_strategies_against_scenarios(price_sets, cvs_employee_options)

def sample_load_file_main(file: str):
    # Example: prices_CVS_20250119_140005.csv
    price_sets = np.loadtxt(file, delimiter=',')
    run_strategies_against_scenarios(price_sets, cvs_employee_options)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sample_full_run_main()
    else:
        sample_load_file_main(sys.argv[1])