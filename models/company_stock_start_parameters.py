class CompanyStockStartParameters:
    def __init__(self, initial_price, expected_rate_of_return, volatility):
        """
            initial_price: The price of the stock at the beginning of the year
            expected_rate_of_return: The expected rate of return of the stock
            volatility: The volatility of the stock
        """
        self.initial_price = initial_price
        self.expected_rate_of_return = expected_rate_of_return
        self.volatility = volatility