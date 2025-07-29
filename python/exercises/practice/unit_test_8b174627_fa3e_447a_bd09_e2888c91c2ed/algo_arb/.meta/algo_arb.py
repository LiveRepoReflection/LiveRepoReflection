import time
import heapq
from collections import defaultdict

def detect_arbitrage_opportunities(quote_stream, transaction_fees, latency_matrix, max_trade_volume, staleness_threshold):
    """
    Detects arbitrage opportunities from a stream of stock quotes.
    
    Args:
        quote_stream: Generator yielding stock quotes
        transaction_fees: Dict mapping exchange IDs to transaction fees
        latency_matrix: Dict of dicts representing latency between exchanges
        max_trade_volume: Maximum volume to trade for each arbitrage opportunity
        staleness_threshold: Maximum age (in ms) for a quote before it's considered stale
    
    Returns:
        List of dictionaries, each representing a profitable arbitrage opportunity
    """
    # Initialize data structures to store the latest quotes
    latest_quotes = {}  # (stock_symbol, exchange_id) -> quote
    timestamps = {}     # (stock_symbol, exchange_id) -> timestamp
    
    # Process all quotes from the stream
    for quote in quote_stream:
        stock = quote["stock_symbol"]
        exchange = quote["exchange_id"]
        
        # Update the latest quote for this stock and exchange
        key = (stock, exchange)
        latest_quotes[key] = quote
        timestamps[key] = quote["timestamp"]
    
    # Find arbitrage opportunities using the latest valid quotes
    return find_arbitrage_opportunities(
        latest_quotes, timestamps, transaction_fees, latency_matrix, 
        max_trade_volume, staleness_threshold
    )

def find_arbitrage_opportunities(latest_quotes, timestamps, transaction_fees, latency_matrix, max_trade_volume, staleness_threshold):
    """
    Finds arbitrage opportunities from the current state of the market.
    
    Args:
        latest_quotes: Dict mapping (stock_symbol, exchange_id) to quote
        timestamps: Dict mapping (stock_symbol, exchange_id) to timestamp
        transaction_fees: Dict mapping exchange IDs to transaction fees
        latency_matrix: Dict of dicts representing latency between exchanges
        max_trade_volume: Maximum volume to trade for each arbitrage opportunity
        staleness_threshold: Maximum age (in ms) for a quote before it's considered stale
    
    Returns:
        List of dictionaries, each representing a profitable arbitrage opportunity
    """
    current_time = int(time.time() * 1000)
    opportunities = []
    
    # Group quotes by stock symbol
    stock_quotes = defaultdict(dict)
    for (stock, exchange), quote in latest_quotes.items():
        # Skip stale quotes
        if current_time - timestamps[(stock, exchange)] > staleness_threshold:
            continue
        
        stock_quotes[stock][exchange] = quote
    
    # For each stock, check for arbitrage opportunities between exchanges
    for stock, exchange_quotes in stock_quotes.items():
        exchanges = list(exchange_quotes.keys())
        
        # Need at least two exchanges to find arbitrage opportunities
        if len(exchanges) < 2:
            continue
        
        # Check all pairs of exchanges for arbitrage opportunities
        for i in range(len(exchanges)):
            exchange_A = exchanges[i]
            quote_A = exchange_quotes[exchange_A]
            
            for j in range(len(exchanges)):
                if i == j:
                    continue
                
                exchange_B = exchanges[j]
                quote_B = exchange_quotes[exchange_B]
                
                # Calculate arbitrage opportunity
                ask_price_A = quote_A["ask_price"]
                bid_price_B = quote_B["bid_price"]
                
                # Calculate total costs
                fee_A = transaction_fees[exchange_A]
                fee_B = transaction_fees[exchange_B]
                latency_AB = latency_matrix[exchange_A][exchange_B]
                latency_BA = latency_matrix[exchange_B][exchange_A]
                
                total_cost = fee_A + fee_B + latency_AB + latency_BA
                profit_per_share = bid_price_B - ask_price_A - total_cost
                
                # If profitable arbitrage exists
                if profit_per_share > 0:
                    # Calculate maximum volume for the trade
                    volume = min(quote_A["volume"], quote_B["volume"], max_trade_volume)
                    total_profit = profit_per_share * volume
                    
                    opportunities.append({
                        "stock_symbol": stock,
                        "exchange_A": exchange_A,
                        "exchange_B": exchange_B,
                        "buy_price": ask_price_A,
                        "sell_price": bid_price_B,
                        "profit": total_profit,
                        "volume": volume
                    })
    
    return opportunities


def optimize_arbitrage_execution(opportunities, max_capital):
    """
    Optimizes arbitrage execution given a list of opportunities and maximum capital.
    
    Args:
        opportunities: List of arbitrage opportunities
        max_capital: Maximum capital available for trading
    
    Returns:
        List of opportunities to execute to maximize profit
    """
    # Sort opportunities by profit per capital ratio (ROI)
    for opp in opportunities:
        opp["capital_required"] = opp["buy_price"] * opp["volume"]
        opp["roi"] = opp["profit"] / opp["capital_required"] if opp["capital_required"] > 0 else 0
    
    # Sort by ROI in descending order
    sorted_opportunities = sorted(opportunities, key=lambda x: x["roi"], reverse=True)
    
    # Greedy algorithm to maximize profit
    selected_opportunities = []
    remaining_capital = max_capital
    
    for opp in sorted_opportunities:
        capital_required = opp["capital_required"]
        
        if capital_required <= remaining_capital:
            selected_opportunities.append(opp)
            remaining_capital -= capital_required
        else:
            # Take partial opportunity if possible
            if remaining_capital > 0:
                fraction = remaining_capital / capital_required
                partial_volume = int(opp["volume"] * fraction)
                
                if partial_volume > 0:
                    partial_opp = opp.copy()
                    partial_opp["volume"] = partial_volume
                    partial_opp["profit"] = partial_opp["profit"] * (partial_volume / opp["volume"])
                    partial_opp["capital_required"] = partial_opp["buy_price"] * partial_volume
                    
                    selected_opportunities.append(partial_opp)
                    remaining_capital = 0
            
            # No more capital
            break
    
    return selected_opportunities


def real_time_arbitrage_monitor(quote_stream, transaction_fees, latency_matrix, max_trade_volume, staleness_threshold, update_interval=100):
    """
    Monitors for arbitrage opportunities in real-time.
    
    Args:
        quote_stream: Generator yielding stock quotes
        transaction_fees: Dict mapping exchange IDs to transaction fees
        latency_matrix: Dict of dicts representing latency between exchanges
        max_trade_volume: Maximum volume to trade for each arbitrage opportunity
        staleness_threshold: Maximum age (in ms) for a quote before it's considered stale
        update_interval: Interval (in ms) between arbitrage opportunity checks
    
    Yields:
        Lists of arbitrage opportunities at regular intervals
    """
    latest_quotes = {}
    timestamps = {}
    last_check_time = 0
    current_time = int(time.time() * 1000)
    
    for quote in quote_stream:
        stock = quote["stock_symbol"]
        exchange = quote["exchange_id"]
        
        # Update the latest quote for this stock and exchange
        key = (stock, exchange)
        latest_quotes[key] = quote
        timestamps[key] = quote["timestamp"]
        
        current_time = int(time.time() * 1000)
        
        # Check for arbitrage opportunities at regular intervals
        if current_time - last_check_time >= update_interval:
            opportunities = find_arbitrage_opportunities(
                latest_quotes, timestamps, transaction_fees, latency_matrix,
                max_trade_volume, staleness_threshold
            )
            
            yield opportunities
            last_check_time = current_time