import heapq
from collections import defaultdict

class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.order_map = {}
        self.next_order_id = 1
        self.transaction_fee = 0.10
        self.min_order_size = 10
        self.price_tick = 0.01
        self.max_inventory = 1000
        self.max_orders = 100

    def update_book(self, timestamp, side, price, size, action):
        if action == 'new':
            if side == 'bid':
                heapq.heappush(self.bids, (-price, timestamp, size))
            else:
                heapq.heappush(self.asks, (price, timestamp, size))
        elif action in ['cancel', 'execute']:
            if side == 'bid':
                self.bids = [order for order in self.bids if order[1] != timestamp or order[0] != -price]
                heapq.heapify(self.bids)
            else:
                self.asks = [order for order in self.asks if order[1] != timestamp or order[0] != price]
                heapq.heapify(self.asks)

    def get_best_bid(self):
        return -self.bids[0][0] if self.bids else 0

    def get_best_ask(self):
        return self.asks[0][0] if self.asks else float('inf')

    def get_spread(self):
        return self.get_best_ask() - self.get_best_bid()

    def validate_order(self, side, price, size, current_inventory, current_capital):
        if size % self.min_order_size != 0:
            return False
        if round(price / self.price_tick) * self.price_tick != price:
            return False
        if side == 'bid' and price >= self.get_best_ask():
            return False
        if side == 'ask' and price <= self.get_best_bid():
            return False
        if side == 'bid' and price * size > current_capital:
            return False
        if side == 'ask' and size > current_inventory:
            return False
        if len(self.order_map) >= self.max_orders:
            return False
        return True

    def generate_order_id(self):
        order_id = self.next_order_id
        self.next_order_id += 1
        return order_id

order_book = OrderBook()

def trade(timestamp, side, price, size, action, current_capital, current_inventory, order_history):
    global order_book
    
    order_book.update_book(timestamp, side, price, size, action)
    
    response = {
        'order_type': 'hold',
        'side': None,
        'price': None,
        'size': None,
        'order_id': None
    }
    
    best_bid = order_book.get_best_bid()
    best_ask = order_book.get_best_ask()
    spread = order_book.get_spread()
    
    if action == 'new' and side == 'bid' and current_inventory < order_book.max_inventory:
        target_price = best_bid - order_book.price_tick
        target_size = min(100, (current_capital // target_price) - 1)
        target_size = max(order_book.min_order_size, target_size - (target_size % order_book.min_order_size))
        
        if order_book.validate_order('bid', target_price, target_size, current_inventory, current_capital):
            order_id = order_book.generate_order_id()
            response = {
                'order_type': 'new',
                'side': 'bid',
                'price': target_price,
                'size': target_size,
                'order_id': order_id
            }
            order_book.order_map[order_id] = {
                'timestamp': timestamp,
                'side': 'bid',
                'price': target_price,
                'size': target_size,
                'status': 'active'
            }
    
    elif action == 'new' and side == 'ask' and current_inventory > 0:
        target_price = best_ask + order_book.price_tick
        target_size = min(100, current_inventory)
        target_size = max(order_book.min_order_size, target_size - (target_size % order_book.min_order_size))
        
        if order_book.validate_order('ask', target_price, target_size, current_inventory, current_capital):
            order_id = order_book.generate_order_id()
            response = {
                'order_type': 'new',
                'side': 'ask',
                'price': target_price,
                'size': target_size,
                'order_id': order_id
            }
            order_book.order_map[order_id] = {
                'timestamp': timestamp,
                'side': 'ask',
                'price': target_price,
                'size': target_size,
                'status': 'active'
            }
    
    elif action == 'cancel' and len(order_book.order_map) > 0:
        for order_id, order in order_book.order_map.items():
            if order['status'] == 'active' and (timestamp - order['timestamp']) > 5000:
                response = {
                    'order_type': 'cancel',
                    'side': None,
                    'price': order['price'],
                    'size': order['size'],
                    'order_id': order_id
                }
                order_book.order_map[order_id]['status'] = 'cancelled'
                break
    
    return response