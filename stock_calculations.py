import numpy as np
from scipy.stats import norm, linregress
from scipy.optimize import brentq

# --- Black-Scholes pricing function ---
def bs_price(S, K, T, r, sigma, option_type='call'):
    """
    Black-Scholes pricing function
    S: stock price
    K: strike price
    T: time to expiration in years
    r: risk-free interest rate
    sigma: volatility
    option_type: 'call' or 'put'
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")
    
    return price

# --- Function to find IV ---
def implied_volatility(S, K, T, r, market_price, option_type='call'):
    """
    Function to find IV
    S: stock price
    K: strike price
    T: time to expiration in years
    r: risk-free interest rate
    market_price: market price of the option
    option_type: 'call' or 'put'
    """
    objective = lambda sigma: bs_price(S, K, T, r, sigma, option_type) - market_price

    iv = brentq(objective, 1e-6, 5.0)  # Solve for IV in [0.000001, 500%]
    return iv
 
def get_expected_rate_of_return_from_capm(stock_price_last_24_months: np.ndarray, spy_last_24_months: np.ndarray, risk_free_rate: float, market_return: float):

    # Calculate monthly returns
    stock_returns = (stock_price_last_24_months[1:] - stock_price_last_24_months[:-1]) / stock_price_last_24_months[:-1]
    spy_returns = (spy_last_24_months[1:] - spy_last_24_months[:-1]) / spy_last_24_months[:-1]

    # Calculate beta
    slope, intercept, r_value, p_value, std_err = linregress(spy_returns, stock_returns)
    beta = slope

    # CAPM formula
    expected_return = risk_free_rate + beta * (market_return - risk_free_rate)

    return float(expected_return)