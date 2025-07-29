import threading

class OrderBook:
    def __init__(self, depth):
        self.depth = depth
        # Aggregated order book for each side: price -> aggregated size
        self.bids = {}
        self.asks = {}
        self.lock = threading.Lock()

    def ingest_update(self, update):
        timestamp = update["timestamp"]
        market_maker = update["market_maker"]
        side = update["side"]
        price = update["price"]
        size = update["size"]
        with self.lock:
            if side == "bid":
                self._ingest_side(self.bids, price, size, is_bid=True)
            elif side == "ask":
                self._ingest_side(self.asks, price, size, is_bid=False)
            else:
                raise ValueError("Side must be 'bid' or 'ask'")

    def _ingest_side(self, book, price, size, is_bid):
        # If level already exists, update cumulative size.
        if price in book:
            new_size = book[price] + size
            if new_size <= 0:
                # Remove level if cumulative size is zero or negative.
                del book[price]
            else:
                book[price] = new_size
        else:
            # Level does not exist.
            # Check if we can insert new price level based on depth constraint.
            if len(book) < self.depth:
                # There is room for this new level.
                if size > 0:
                    book[price] = size
            else:
                # Book is at capacity, determine if new level qualifies.
                # For bid: we only keep the highest prices so, the worst bid is the minimum.
                # For ask: we only keep the lowest prices so, the worst ask is the maximum.
                if is_bid:
                    worst_price = min(book.keys())
                    if price > worst_price and size > 0:
                        # Insert new level and remove the worst level.
                        book[price] = size
                        # Re-check capacity: remove the lowest price level.
                        if len(book) > self.depth:
                            worst_price = min(book.keys())
                            del book[worst_price]
                    # Else, discard update.
                else:
                    worst_price = max(book.keys())
                    if price < worst_price and size > 0:
                        book[price] = size
                        if len(book) > self.depth:
                            worst_price = max(book.keys())
                            del book[worst_price]
                    # Else, discard update.

    def get_top_levels(self, side, depth):
        with self.lock:
            if side == "bid":
                # For bids, sort in descending order (highest price first)
                sorted_levels = sorted(self.bids.items(), key=lambda x: x[0], reverse=True)
            elif side == "ask":
                # For asks, sort in ascending order (lowest price first)
                sorted_levels = sorted(self.asks.items(), key=lambda x: x[0])
            else:
                raise ValueError("Side must be 'bid' or 'ask'")
            # Return only up to the top 'depth' levels.
            return sorted_levels[:depth]

    def get_weighted_average_price(self, side):
        with self.lock:
            if side == "bid":
                book = self.bids
            elif side == "ask":
                book = self.asks
            else:
                raise ValueError("Side must be 'bid' or 'ask'")
            
            total_size = sum(book.values())
            if total_size <= 0:
                return 0.0
            weighted_sum = sum(price * size for price, size in book.items())
            return weighted_sum / total_size