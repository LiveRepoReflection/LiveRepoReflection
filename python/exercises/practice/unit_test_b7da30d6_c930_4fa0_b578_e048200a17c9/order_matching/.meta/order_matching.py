from collections import defaultdict
import heapq
from typing import List, Tuple, Dict, Set

class OrderBook:
    def __init__(self):
        self.price_levels: Dict[int, List[Tuple[int, str, int]]] = defaultdict(list)
        self.order_map: Dict[str, Tuple[int, int, int]] = {}  # order_id -> (price, timestamp, quantity)
        self.timestamp = 0

    def add(self, order_id: str, price: int, quantity: int) -> None:
        self.timestamp += 1
        self.order_map[order_id] = (price, self.timestamp, quantity)
        heapq.heappush(self.price_levels[price], (self.timestamp, order_id, quantity))

    def remove(self, order_id: str) -> None:
        if order_id not in self.order_map:
            raise ValueError(f"Order {order_id} not found")
        price, _, _ = self.order_map[order_id]
        del self.order_map[order_id]
        
        # Remove the order from price_levels
        self.price_levels[price] = [
            order for order in self.price_levels[price]
            if order[1] != order_id
        ]
        if not self.price_levels[price]:
            del self.price_levels[price]

    def update_quantity(self, order_id: str, new_quantity: int) -> None:
        price, timestamp, _ = self.order_map[order_id]
        self.order_map[order_id] = (price, timestamp, new_quantity)
        
        # Update quantity in price_levels
        for i, order in enumerate(self.price_levels[price]):
            if order[1] == order_id:
                self.price_levels[price][i] = (timestamp, order_id, new_quantity)
                break

    def get_best_price(self) -> int:
        if not self.price_levels:
            return None
        return next(iter(sorted(self.price_levels.keys())))

    def get_orders_at_price(self, price: int) -> List[Tuple[str, int]]:
        if price not in self.price_levels:
            return []
        return [(order[1], order[2]) for order in sorted(self.price_levels[price])]

class MatchingEngine:
    def __init__(self):
        self.buy_book = OrderBook()
        self.sell_book = OrderBook()
        self.trades: List[Tuple[str, str, int, int]] = []
        self.existing_orders: Set[str] = set()

    def validate_order(self, order: Tuple[str, str, int, int]) -> None:
        order_id, order_type, price, quantity = order
        
        if order_id in self.existing_orders:
            raise ValueError(f"Duplicate order ID: {order_id}")
        if order_type not in ["BUY", "SELL"]:
            raise ValueError(f"Invalid order type: {order_type}")
        if price <= 0:
            raise ValueError(f"Invalid price: {price}")
        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}")

    def try_match(self, buy_order_id: str, sell_order_id: str,
                  price: int, quantity: int) -> None:
        self.trades.append((buy_order_id, sell_order_id, price, quantity))

    def add_order(self, order: Tuple[str, str, int, int]) -> None:
        order_id, order_type, price, quantity = order
        self.validate_order(order)
        self.existing_orders.add(order_id)

        if order_type == "BUY":
            while quantity > 0:
                best_sell_price = self.sell_book.get_best_price()
                if best_sell_price is None or best_sell_price > price:
                    break

                sell_orders = self.sell_book.get_orders_at_price(best_sell_price)
                if not sell_orders:
                    break

                for sell_order_id, sell_quantity in sell_orders:
                    match_quantity = min(quantity, sell_quantity)
                    self.try_match(order_id, sell_order_id, best_sell_price, match_quantity)

                    if sell_quantity == match_quantity:
                        self.sell_book.remove(sell_order_id)
                    else:
                        self.sell_book.update_quantity(sell_order_id, sell_quantity - match_quantity)

                    quantity -= match_quantity
                    if quantity == 0:
                        break

            if quantity > 0:
                self.buy_book.add(order_id, price, quantity)

        else:  # SELL order
            while quantity > 0:
                best_buy_price = self.buy_book.get_best_price()
                if best_buy_price is None or best_buy_price < price:
                    break

                buy_orders = self.buy_book.get_orders_at_price(best_buy_price)
                if not buy_orders:
                    break

                for buy_order_id, buy_quantity in buy_orders:
                    match_quantity = min(quantity, buy_quantity)
                    self.try_match(buy_order_id, order_id, price, match_quantity)

                    if buy_quantity == match_quantity:
                        self.buy_book.remove(buy_order_id)
                    else:
                        self.buy_book.update_quantity(buy_order_id, buy_quantity - match_quantity)

                    quantity -= match_quantity
                    if quantity == 0:
                        break

            if quantity > 0:
                self.sell_book.add(order_id, price, quantity)

    def cancel_order(self, order_id: str) -> None:
        if order_id not in self.existing_orders:
            raise ValueError(f"Order {order_id} not found")
        
        try:
            self.buy_book.remove(order_id)
        except ValueError:
            try:
                self.sell_book.remove(order_id)
            except ValueError:
                raise ValueError(f"Order {order_id} not found in order books")
        
        self.existing_orders.remove(order_id)

    def get_order_book(self) -> Tuple[List[Tuple[str, str, int, int]], 
                                     List[Tuple[str, str, int, int]]]:
        buy_orders = []
        sell_orders = []

        # Get buy orders sorted by price (highest first) and time
        for price in sorted(self.buy_book.price_levels.keys(), reverse=True):
            for _, order_id, quantity in sorted(self.buy_book.price_levels[price]):
                buy_orders.append((order_id, "BUY", price, quantity))

        # Get sell orders sorted by price (lowest first) and time
        for price in sorted(self.sell_book.price_levels.keys()):
            for _, order_id, quantity in sorted(self.sell_book.price_levels[price]):
                sell_orders.append((order_id, "SELL", price, quantity))

        return buy_orders, sell_orders

    def get_trades(self) -> List[Tuple[str, str, int, int]]:
        return self.trades.copy()