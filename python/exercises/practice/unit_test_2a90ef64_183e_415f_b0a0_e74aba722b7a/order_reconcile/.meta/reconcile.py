def reconcile(order_books):
    """
    Reconcile multiple order books into a single order book.
    Each order book is a dict with keys "bids" and "asks", each being a list of tuples (price, quantity, order_id).
    The function merges unique orders, resolves quantity discrepancies by taking the maximum quantity for the same order_id,
    sorts bids in descending order by price (with tie-breaker: lower order_id comes first),
    and sorts asks in ascending order by price (with tie-breaker: lower order_id comes first).
    """
    reconciled_bids = {}
    reconciled_asks = {}

    for book in order_books:
        bids = book.get("bids", [])
        asks = book.get("asks", [])
        
        for order in bids:
            price, quantity, order_id = order
            # If the order already exists, update the quantity if the new quantity is larger
            if order_id in reconciled_bids:
                existing_price, existing_quantity, _ = reconciled_bids[order_id]
                if quantity > existing_quantity:
                    reconciled_bids[order_id] = (price, quantity, order_id)
            else:
                reconciled_bids[order_id] = (price, quantity, order_id)
        
        for order in asks:
            price, quantity, order_id = order
            if order_id in reconciled_asks:
                existing_price, existing_quantity, _ = reconciled_asks[order_id]
                if quantity > existing_quantity:
                    reconciled_asks[order_id] = (price, quantity, order_id)
            else:
                reconciled_asks[order_id] = (price, quantity, order_id)

    # Convert dictionaries to lists
    bids_list = list(reconciled_bids.values())
    asks_list = list(reconciled_asks.values())

    # Sort bids: descending by price, and if equal, ascending by order_id
    bids_list.sort(key=lambda order: (-order[0], order[2]))
    # Sort asks: ascending by price, and if equal, ascending by order_id
    asks_list.sort(key=lambda order: (order[0], order[2]))

    return {"bids": bids_list, "asks": asks_list}

if __name__ == '__main__':
    # Manual test run
    sample_books = [
        {
            "bids": [(100.0, 5, "order1"), (99.5, 3, "order2")],
            "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
        },
        {
            "bids": [(100.0, 5, "order1"), (99.0, 2, "order5")],
            "asks": [(101.0, 2, "order3"), (102.0, 1, "order6")]
        },
        {
            "bids": [(100.0, 5, "order1")],
            "asks": [(101.0, 2, "order3"), (101.5, 4, "order4")]
        }
    ]
    result = reconcile(sample_books)
    print(result)