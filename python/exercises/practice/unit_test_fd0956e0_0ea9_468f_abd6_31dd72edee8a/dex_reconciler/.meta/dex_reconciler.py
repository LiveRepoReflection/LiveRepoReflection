from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any
import threading
import heapq

class OrderBook:
    def __init__(self):
        self.bids = []  # max heap for bids
        self.asks = []  # min heap for asks
        self.last_update = None

    def update(self, bids: List[Dict[str, Decimal]], asks: List[Dict[str, Decimal]], timestamp: datetime):
        self.bids = [(-bid['price'], bid['quantity']) for bid in bids]
        self.asks = [(ask['price'], ask['quantity']) for ask in asks]
        heapq.heapify(self.bids)
        heapq.heapify(self.asks)
        self.last_update = timestamp

    def get_best_bid(self) -> tuple:
        return (-self.bids[0][0], self.bids[0][1]) if self.bids else (None, None)

    def get_best_ask(self) -> tuple:
        return self.asks[0] if self.asks else (None, None)

class DEXReconciler:
    def __init__(self, num_dexes: int, 
                 price_threshold: Decimal = Decimal('0.1'),
                 quantity_threshold: Decimal = Decimal('0.1'),
                 stale_threshold: timedelta = timedelta(seconds=5)):
        if not 1 <= num_dexes <= 100:
            raise ValueError("Number of DEXs must be between 1 and 100")
        
        self.num_dexes = num_dexes
        self.price_threshold = price_threshold
        self.quantity_threshold = quantity_threshold
        self.stale_threshold = stale_threshold
        self.order_books = {i+1: OrderBook() for i in range(num_dexes)}
        self.lock = threading.Lock()

    def _validate_precision(self, value: Decimal) -> bool:
        return len(str(value).split('.')[-1]) <= 8 if '.' in str(value) else True

    def _validate_snapshot(self, snapshot: Dict[str, Any]) -> None:
        if not 1 <= snapshot['dex_id'] <= self.num_dexes:
            raise ValueError(f"Invalid DEX ID: {snapshot['dex_id']}")

        for order_list in [snapshot['bids'], snapshot['asks']]:
            for order in order_list:
                if not (self._validate_precision(order['price']) and 
                       self._validate_precision(order['quantity'])):
                    raise ValueError("Price and quantity must have at most 8 decimal places")

    def process_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        self._validate_snapshot(snapshot)
        
        with self.lock:
            order_book = self.order_books[snapshot['dex_id']]
            order_book.update(snapshot['bids'], snapshot['asks'], snapshot['timestamp'])
        
        return True

    def find_price_discrepancies(self) -> List[Dict[str, Any]]:
        discrepancies = []
        with self.lock:
            for dex1 in range(1, self.num_dexes + 1):
                for dex2 in range(dex1 + 1, self.num_dexes + 1):
                    ob1 = self.order_books[dex1]
                    ob2 = self.order_books[dex2]
                    
                    bid1_price, _ = ob1.get_best_bid()
                    bid2_price, _ = ob2.get_best_bid()
                    ask1_price, _ = ob1.get_best_ask()
                    ask2_price, _ = ob2.get_best_ask()

                    if all(p is not None for p in [bid1_price, bid2_price, ask1_price, ask2_price]):
                        bid_diff = abs(bid1_price - bid2_price)
                        ask_diff = abs(ask1_price - ask2_price)

                        if bid_diff > self.price_threshold or ask_diff > self.price_threshold:
                            discrepancies.append({
                                'dex1': dex1,
                                'dex2': dex2,
                                'bid_difference': str(bid_diff),
                                'ask_difference': str(ask_diff),
                                'timestamp': datetime.now()
                            })

        return discrepancies

    def find_quantity_discrepancies(self) -> List[Dict[str, Any]]:
        discrepancies = []
        with self.lock:
            for dex1 in range(1, self.num_dexes + 1):
                for dex2 in range(dex1 + 1, self.num_dexes + 1):
                    ob1 = self.order_books[dex1]
                    ob2 = self.order_books[dex2]
                    
                    _, bid1_qty = ob1.get_best_bid()
                    _, bid2_qty = ob2.get_best_bid()
                    _, ask1_qty = ob1.get_best_ask()
                    _, ask2_qty = ob2.get_best_ask()

                    if all(q is not None for q in [bid1_qty, bid2_qty, ask1_qty, ask2_qty]):
                        bid_qty_diff = abs(bid1_qty - bid2_qty)
                        ask_qty_diff = abs(ask1_qty - ask2_qty)

                        if bid_qty_diff > self.quantity_threshold or ask_qty_diff > self.quantity_threshold:
                            discrepancies.append({
                                'dex1': dex1,
                                'dex2': dex2,
                                'bid_quantity_difference': str(bid_qty_diff),
                                'ask_quantity_difference': str(ask_qty_diff),
                                'timestamp': datetime.now()
                            })

        return discrepancies

    def find_stale_orders(self) -> List[Dict[str, Any]]:
        stale_orders = []
        current_time = datetime.now()
        
        with self.lock:
            for dex_id, order_book in self.order_books.items():
                if (order_book.last_update and 
                    current_time - order_book.last_update > self.stale_threshold):
                    stale_orders.append({
                        'dex_id': dex_id,
                        'last_update': order_book.last_update,
                        'staleness': str(current_time - order_book.last_update)
                    })

        return stale_orders

    def generate_report(self) -> Dict[str, Any]:
        return {
            'price_discrepancies': self.find_price_discrepancies(),
            'quantity_discrepancies': self.find_quantity_discrepancies(),
            'stale_orders': self.find_stale_orders(),
            'timestamp': datetime.now(),
            'total_dexes': self.num_dexes
        }