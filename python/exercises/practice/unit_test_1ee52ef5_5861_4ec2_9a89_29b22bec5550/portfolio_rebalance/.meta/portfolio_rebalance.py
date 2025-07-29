def rebalance_portfolio(
    target_allocation,
    current_holdings,
    price_update,
    transaction_cost_rate,
    min_trade_size,
    max_trade_value,
    rebalancing_interval,
    price_update_counter
):
    """
    Rebalance a stock portfolio based on target allocations and constraints.
    
    Args:
        target_allocation (dict): The desired asset allocation (symbol -> percentage).
        current_holdings (dict): The current stock holdings (symbol -> shares).
        price_update (dict): The current stock price update (symbol -> price).
        transaction_cost_rate (float): The transaction cost rate.
        min_trade_size (int): The minimum trade size (in shares).
        max_trade_value (float): The maximum trade value per order.
        rebalancing_interval (int): Number of price updates between rebalancing.
        price_update_counter (int): Counter of price updates since last rebalance.
    
    Returns:
        tuple: (orders, updated_holdings, updated_counter)
            orders (list): List of tuples (symbol, shares) for trades
            updated_holdings (dict): Updated holdings after trades
            updated_counter (int): Updated price update counter
    """
    # Check if it's time to rebalance
    if price_update_counter < rebalancing_interval:
        # Not time yet, just increment counter and return
        return [], current_holdings, price_update_counter + 1
    
    # Reset counter as we're now rebalancing
    updated_counter = 0
    
    # If either target_allocation or current_holdings is empty, no action needed
    if not target_allocation or not current_holdings:
        return [], current_holdings, updated_counter
    
    # Check if we have prices for all stocks in both target and current holdings
    all_symbols = set(list(target_allocation.keys()) + list(current_holdings.keys()))
    if not all(symbol in price_update for symbol in all_symbols):
        # Missing price data, cannot rebalance safely
        return [], current_holdings, updated_counter
    
    # Calculate current portfolio value
    portfolio_value = sum(
        current_holdings.get(symbol, 0) * price_update[symbol]
        for symbol in all_symbols
    )
    
    # If portfolio is empty, cannot rebalance
    if portfolio_value == 0:
        return [], current_holdings, updated_counter
    
    # Calculate current allocations
    current_allocation = {
        symbol: (current_holdings.get(symbol, 0) * price_update[symbol]) / portfolio_value
        for symbol in all_symbols
    }
    
    # Calculate target value for each stock
    target_values = {
        symbol: target_allocation.get(symbol, 0) * portfolio_value
        for symbol in all_symbols
    }
    
    # Calculate the ideal number of shares for each stock
    ideal_shares = {
        symbol: int(target_values[symbol] / price_update[symbol])
        for symbol in all_symbols
        if price_update[symbol] > 0  # Avoid division by zero
    }
    
    # Calculate the initial orders without constraints
    unconstrained_orders = [
        (symbol, ideal_shares[symbol] - current_holdings.get(symbol, 0))
        for symbol in all_symbols
        if symbol in ideal_shares and ideal_shares[symbol] != current_holdings.get(symbol, 0)
    ]
    
    # Apply minimum trade size constraint
    orders = [
        (symbol, shares) for symbol, shares in unconstrained_orders
        if abs(shares) >= min_trade_size
    ]
    
    # Apply transaction cost consideration and maximum trade value constraint
    adjusted_orders = []
    remaining_portfolio_value = portfolio_value
    
    # Sort orders by descending trade value (importance)
    sorted_orders = sorted(
        orders,
        key=lambda order: abs(order[1] * price_update[order[0]]),
        reverse=True
    )
    
    for symbol, shares in sorted_orders:
        price = price_update[symbol]
        trade_value = abs(shares * price)
        
        # Apply transaction cost adjustment
        transaction_cost = trade_value * transaction_cost_rate
        
        # If this trade would make the portfolio worse due to costs, skip it
        current_deviation = abs(
            current_allocation.get(symbol, 0) - target_allocation.get(symbol, 0)
        )
        
        # Calculate new allocation after the trade
        new_shares = current_holdings.get(symbol, 0) + shares
        new_value = new_shares * price
        adjusted_portfolio_value = remaining_portfolio_value - transaction_cost
        
        if adjusted_portfolio_value <= 0:
            continue  # Skip this trade if it would deplete the portfolio
        
        new_allocation = new_value / adjusted_portfolio_value
        new_deviation = abs(new_allocation - target_allocation.get(symbol, 0))
        
        # Only trade if it improves the allocation (considering costs)
        # For stocks not in target, always sell
        proceed_with_trade = (
            (new_deviation < current_deviation) or 
            (target_allocation.get(symbol, 0) == 0 and shares < 0)
        )
        
        if not proceed_with_trade:
            continue
        
        # Apply maximum trade value constraint
        if trade_value > max_trade_value:
            # Adjust the shares to respect the max_trade_value
            adjusted_shares = int((max_trade_value / price) * (1 if shares > 0 else -1))
            if abs(adjusted_shares) < min_trade_size:
                continue  # Skip if adjusted order falls below min_trade_size
            shares = adjusted_shares
        
        adjusted_orders.append((symbol, shares))
        
        # Update the remaining portfolio value
        trade_value = abs(shares * price)
        transaction_cost = trade_value * transaction_cost_rate
        remaining_portfolio_value -= transaction_cost
    
    # Update holdings based on executed orders
    updated_holdings = current_holdings.copy()
    for symbol, shares in adjusted_orders:
        if symbol in updated_holdings:
            updated_holdings[symbol] += shares
            if updated_holdings[symbol] == 0:
                del updated_holdings[symbol]  # Remove stocks with zero shares
        else:
            updated_holdings[symbol] = shares
    
    return adjusted_orders, updated_holdings, updated_counter