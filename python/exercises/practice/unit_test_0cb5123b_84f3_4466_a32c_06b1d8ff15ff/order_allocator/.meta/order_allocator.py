from typing import Dict, List, Tuple
import heapq

def allocate_market_order(
    order_book: Dict[int, List[str]],
    order_quantities: Dict[str, int],
    market_buy_order: int
) -> List[Tuple[str, int]]:
    """
    Allocates a market buy order against the order book following price-time priority.
    
    Args:
        order_book: Dictionary mapping prices to lists of order IDs
        order_quantities: Dictionary mapping order IDs to their quantities
        market_buy_order: Quantity to buy
    
    Returns:
        List of tuples containing (order_id, filled_quantity)
    """
    if not order_book or market_buy_order <= 0:
        return []

    # Create min heap of prices for efficient access to best prices
    prices = list(order_book.keys())
    heapq.heapify(prices)
    
    remaining_quantity = market_buy_order
    allocations = []
    
    # Process orders from lowest to highest price
    while prices and remaining_quantity > 0:
        current_price = heapq.heappop(prices)
        order_ids = order_book[current_price]
        
        # Process all orders at current price level
        for order_id in order_ids:
            available_quantity = order_quantities[order_id]
            
            if remaining_quantity <= 0:
                break
                
            # Calculate fill quantity
            fill_quantity = min(remaining_quantity, available_quantity)
            
            if fill_quantity > 0:
                allocations.append((order_id, fill_quantity))
                remaining_quantity -= fill_quantity
    
    return allocations