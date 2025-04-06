import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import math

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
 