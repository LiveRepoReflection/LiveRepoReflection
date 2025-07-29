def optimal_fulfillment_order(orders, items_size):
    """
    Calculates the optimal order fulfillment sequence to minimize total waiting time.
    Implements the Shortest Processing Time first (SPT) algorithm which is optimal
    for minimizing total completion time in single-machine scheduling.
    
    Args:
        orders (list): A list of order dictionaries.
        items_size (dict): A dictionary mapping item_id to its size.

    Returns:
        list: A list of order_id's representing the optimal fulfillment order.
    """
    if not orders:
        return []

    # Calculate fulfillment time for each order
    order_times = []
    for order in orders:
        fulfillment_time = 0
        for item_id, quantity in order['items'].items():
            if item_id not in items_size:
                raise ValueError(f"Item {item_id} not found in items_size")
            fulfillment_time += quantity * items_size[item_id]
        order_times.append((order['order_id'], fulfillment_time))

    # Sort orders by fulfillment time (shortest first)
    order_times.sort(key=lambda x: x[1])

    # Extract just the order_ids in optimal sequence
    return [order_id for order_id, _ in order_times]