from models.employee_options import EmployeeOptions
from constants_company_plans import cvs_stock_plan

cvs_employee_options = EmployeeOptions(
    company_stock_plan=cvs_stock_plan,
    max_contribution=1947.51,
    steps_to_zero=0,
    liquidity_preference_rate=0.05,
    capital_gains_tax_rate=0.15
)