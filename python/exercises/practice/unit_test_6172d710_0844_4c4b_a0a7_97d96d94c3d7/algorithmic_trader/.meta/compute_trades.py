import bisect

def compute_trades(predictions, initial_capital, transaction_cost, risk_aversion, max_holdings, min_trade_size, stock_price_history):
    def get_latest_price(timestamp, history):
        # Extract timestamps from history
        times = [t for t, price in history]
        idx = bisect.bisect_left(times, timestamp) - 1
        if idx < 0:
            raise ValueError("No stock price available before the prediction timestamp.")
        return history[idx][1]

    def to_multiple(x, multiple):
        return (x // multiple) * multiple

    capital = initial_capital
    holdings = 0
    trades = []

    for pred in predictions:
        pred_timestamp, probability, expected_return = pred
        price = get_latest_price(pred_timestamp, stock_price_history)

        margin = probability * expected_return
        trade = 0

        # Decision to buy when expected_return is positive and margin overcomes risk_aversion
        if expected_return > 0 and margin > risk_aversion * 0.05:
            # Maximum shares affordable and room to buy shares
            affordable = int(capital // (price * (1 + transaction_cost)))
            space = max_holdings - holdings
            max_possible = min(affordable, space)
            if max_possible >= min_trade_size:
                # Scale purchase by confidence factor bounded by 1
                factor = min(margin, 1.0)
                proposed = int(max_possible * factor)
                proposed = to_multiple(proposed, min_trade_size)
                if proposed >= min_trade_size:
                    trade = proposed
        # Decision to sell when expected_return is negative and signal is strong
        elif expected_return < 0 and -margin > risk_aversion * 0.05:
            if holdings >= min_trade_size:
                factor = min(-margin, 1.0)
                proposed = int(holdings * factor)
                proposed = to_multiple(proposed, min_trade_size)
                if proposed >= min_trade_size:
                    trade = -proposed
        else:
            trade = 0

        # Execute the trade and update portfolio
        if trade > 0:
            cost = trade * price * (1 + transaction_cost)
            if cost <= capital and (holdings + trade) <= max_holdings:
                capital -= cost
                holdings += trade
            else:
                trade = 0
        elif trade < 0:
            if abs(trade) <= holdings:
                revenue = abs(trade) * price * (1 - transaction_cost)
                capital += revenue
                holdings += trade  # trade is negative, so subtraction
            else:
                trade = 0

        trades.append(trade)

    return trades