from decimal import Decimal
from typing import Dict, List, Tuple, Set
import heapq

def find_optimal_trade_route(
    graph: Dict[str, List[Tuple[str, float]]],
    start_currency: str,
    target_currency: str,
    initial_amount: float,
    max_hops: int,
    min_profit: float
) -> float:
    """
    Find the optimal trading route that maximizes the final amount of target currency.
    Uses a modified Dijkstra's algorithm with additional constraints and cycle detection.
    """
    if initial_amount == 0.0:
        return 0.0
    
    if start_currency == target_currency:
        return initial_amount if -min_profit <= 0 else 0.0
    
    # Convert initial amount to Decimal for better precision
    initial_amount = Decimal(str(initial_amount))
    
    # Priority queue: (-current_amount, currency, hops, visited)
    # Using negative amount for max-heap behavior
    pq = [(-initial_amount, start_currency, 0, {start_currency})]
    heapq.heapify(pq)
    
    # Keep track of best amount for each (currency, hops) combination
    best_amounts = {(start_currency, 0): initial_amount}
    
    best_result = Decimal('0')
    
    while pq:
        neg_amount, curr, hops, visited = heapq.heappop(pq)
        amount = -neg_amount
        
        # Skip if we've found a better result already
        if amount < best_amounts.get((curr, hops), Decimal('-inf')):
            continue
        
        # Check if we reached target_currency
        if curr == target_currency:
            best_result = max(best_result, amount)
            continue
        
        # Stop if we reached max_hops
        if hops >= max_hops:
            continue
        
        # Try all possible trades
        for next_curr, rate in graph.get(curr, []):
            rate = Decimal(str(rate))
            new_amount = amount * rate
            
            # Skip if the trade would result in a worse amount than we've seen
            if new_amount <= best_amounts.get((next_curr, hops + 1), Decimal('-inf')):
                continue
            
            # Handle cycles: allow revisiting a currency if it leads to better results
            # but limit the number of revisits to prevent infinite loops
            if next_curr in visited and len(visited) > max_hops // 2:
                continue
                
            new_visited = visited | {next_curr}
            
            # Update best amount for this currency and number of hops
            best_amounts[(next_curr, hops + 1)] = new_amount
            
            # Add to priority queue
            heapq.heappush(pq, (-new_amount, next_curr, hops + 1, new_visited))
    
    # Convert best result to float and check profit threshold
    final_result = float(best_result)
    if final_result - float(initial_amount) >= min_profit:
        return final_result
    return 0.0