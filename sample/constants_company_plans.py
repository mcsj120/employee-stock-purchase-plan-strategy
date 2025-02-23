from models.company_plan import CompanyStockPlan

cvs_stock_plan = CompanyStockPlan(
    name='CVS',
    discount_rate=0.9,
    offering_periods=2.0,
    pay_periods_per_offering=12.0,
    cost_to_sell=7.0
)
