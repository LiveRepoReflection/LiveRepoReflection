import heapq
from collections import defaultdict

class OrderMatchingEngine:
    def __init__(self):
        self.buy_orders = []  # Max-heap for buy orders (using negative prices)
        self.sell_orders = []  # Min-heap for sell orders
        self.orders = {}  # order_id -> order details
        self.order_status = defaultdict(lambda: (0, False))  # order_id -> (filled_quantity, is_cancelled)
        self.price_levels_buy = defaultdict(list)  # price -> [orders]
        self.price_levels_sell = defaultdict(list)  # price -> [orders]
        self.active_orders = set()  # Set of active order IDs

    def add_order(self, order_id, order_type, price, quantity, timestamp):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if order_id in self.active_orders:
            raise ValueError("Duplicate order ID")
        
        self.active_orders.add(order_id)
        order = {
            'id': order_id,
            'type': order_type,
            'price': price,
            'quantity': quantity,
            'remaining': quantity,
            'timestamp': timestamp
        }
        self.orders[order_id] = order
        
        if order_type == "BUY":
            self._add_buy_order(order)
            self._match_orders()
        else:
            self._add_sell_order(order)
            self._match_orders()

    def _add_buy_order(self, order):
        heapq.heappush(self.buy_orders, (-order['price'], order['timestamp'], order['id']))
        self.price_levels_buy[order['price']].append(order)

    def _add_sell_order(self, order):
        heapq.heappush(self.sell_orders, (order['price'], order['timestamp'], order['id']))
        self.price_levels_sell[order['price']].append(order)

    def _match_orders(self):
        while self.buy_orders and self.sell_orders:
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]
            
            buy_price = -best_buy[0]
            sell_price = best_sell[0]
            
            if buy_price >= sell_price:
                # Get the actual order objects
                buy_order = self.price_levels_buy[buy_price][0]
                sell_order = self.price_levels_sell[sell_price][0]
                
                # Determine trade quantity
                trade_qty = min(buy_order['remaining'], sell_order['remaining'])
                
                # Execute the trade
                self._process_trade(buy_order, sell_order, trade_qty)
                
                # Clean up fully filled orders
                if buy_order['remaining'] == 0:
                    self._remove_buy_order(buy_order)
                if sell_order['remaining'] == 0:
                    self._remove_sell_order(sell_order)
            else:
                break

    def _process_trade(self, buy_order, sell_order, quantity):
        buy_order['remaining'] -= quantity
        sell_order['remaining'] -= quantity
        
        # Update order status
        self.order_status[buy_order['id']] = (buy_order['quantity'] - buy_order['remaining'], False)
        self.order_status[sell_order['id']] = (sell_order['quantity'] - sell_order['remaining'], False)

    def _remove_buy_order(self, order):
        price = order['price']
        self.price_levels_buy[price].remove(order)
        if not self.price_levels_buy[price]:
            del self.price_levels_buy[price]
            # Rebuild heap to remove the price level
            self.buy_orders = [(-p, t, oid) for p in self.price_levels_buy for o in self.price_levels_buy[p] for t, oid in [(o['timestamp'], o['id'])]]
            heapq.heapify(self.buy_orders)

    def _remove_sell_order(self, order):
        price = order['price']
        self.price_levels_sell[price].remove(order)
        if not self.price_levels_sell[price]:
            del self.price_levels_sell[price]
            # Rebuild heap to remove the price level
            self.sell_orders = [(p, t, oid) for p in self.price_levels_sell for o in self.price_levels_sell[p] for t, oid in [(o['timestamp'], o['id'])]]
            heapq.heapify(self.sell_orders)

    def cancel_order(self, order_id):
        if order_id not in self.active_orders:
            return False
        
        order = self.orders[order_id]
        if order['remaining'] == 0:
            return False
        
        if order['type'] == "BUY":
            self._remove_buy_order(order)
        else:
            self._remove_sell_order(order)
        
        self.order_status[order_id] = (order['quantity'] - order['remaining'], True)
        self.active_orders.remove(order_id)
        return True

    def get_order_status(self, order_id):
        return self.order_status[order_id]

    def get_market_depth(self, levels):
        # Get top buy levels (sorted descending)
        buy_prices = sorted(self.price_levels_buy.keys(), reverse=True)[:levels]
        buy_depth = [(p, sum(o['remaining'] for o in self.price_levels_buy[p])) for p in buy_prices]
        
        # Get top sell levels (sorted ascending)
        sell_prices = sorted(self.price_levels_sell.keys())[:levels]
        sell_depth = [(p, sum(o['remaining'] for o in self.price_levels_sell[p])) for p in sell_prices]
        
        return (buy_depth, sell_depth)