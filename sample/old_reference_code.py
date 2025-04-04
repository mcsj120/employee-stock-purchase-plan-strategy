from constants import MAX_PRICE_IRS
from models.company_plan import CompanyStockPlan

from constants_company_plans import cvs_stock_plan


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


print(f'The baseline value for scenario {function_name} is {running_ESPPResult.baseline_value_sum/len(prices)}')
print(f'The average total value for the espp plan for scenario {function_name} is {running_ESPPResult.total_value_sum/len(prices)}')
print(f'The average money_contributed for the espp plan for scenario {function_name} is {running_ESPPResult.money_contributed_sum/len(prices)}')
print(f'The average roi for the espp plan for scenario {function_name} is {running_ESPPResult.roi_sum/len(prices)}')
print(f'The average money refunded for the espp plan for scenario {function_name} is {running_ESPPResult.money_refunded_sum/len(prices)}')