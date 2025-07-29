import unittest
from hft_strategy import trade

class TestHFTStrategy(unittest.TestCase):
    def setUp(self):
        self.initial_capital = 1000000.0
        self.initial_inventory = 0
        self.order_history = {}

    def test_no_action_on_empty_update(self):
        result = trade(
            timestamp=1000,
            side=None,
            price=None,
            size=None,
            action=None,
            current_capital=self.initial_capital,
            current_inventory=self.initial_inventory,
            order_history=self.order_history
        )
        self.assertEqual(result['order_type'], 'hold')

    def test_new_bid_order(self):
        result = trade(
            timestamp=1000,
            side='bid',
            price=100.0,
            size=100,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=self.initial_inventory,
            order_history=self.order_history
        )
        self.assertIn(result['order_type'], ['new', 'hold'])
        if result['order_type'] == 'new':
            self.assertEqual(result['side'], 'bid')
            self.assertTrue(0 < result['price'] <= 100.0)
            self.assertTrue(result['size'] % 10 == 0)

    def test_new_ask_order_with_inventory(self):
        result = trade(
            timestamp=1000,
            side='ask',
            price=101.0,
            size=50,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=100,
            order_history=self.order_history
        )
        self.assertIn(result['order_type'], ['new', 'hold'])
        if result['order_type'] == 'new':
            self.assertEqual(result['side'], 'ask')
            self.assertTrue(result['price'] >= 101.0)
            self.assertTrue(result['size'] % 10 == 0)
            self.assertTrue(result['size'] <= 100)

    def test_order_cancellation(self):
        order_id = 1
        self.order_history = {
            order_id: {
                'order_id': order_id,
                'timestamp': 500,
                'side': 'bid',
                'price': 99.0,
                'size': 100,
                'status': 'active'
            }
        }
        result = trade(
            timestamp=1000,
            side='bid',
            price=99.0,
            size=100,
            action='cancel',
            current_capital=self.initial_capital,
            current_inventory=self.initial_inventory,
            order_history=self.order_history
        )
        self.assertIn(result['order_type'], ['cancel', 'hold'])

    def test_inventory_constraint(self):
        result = trade(
            timestamp=1000,
            side='bid',
            price=100.0,
            size=100,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=1000,
            order_history=self.order_history
        )
        self.assertEqual(result['order_type'], 'hold')

    def test_capital_constraint(self):
        result = trade(
            timestamp=1000,
            side='bid',
            price=1000.0,
            size=1000,
            action='new',
            current_capital=1000.0,
            current_inventory=0,
            order_history=self.order_history
        )
        self.assertEqual(result['order_type'], 'hold')

    def test_order_size_multiple(self):
        result = trade(
            timestamp=1000,
            side='bid',
            price=100.0,
            size=100,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=0,
            order_history=self.order_history
        )
        if result['order_type'] == 'new':
            self.assertEqual(result['size'] % 10, 0)

    def test_price_increment_constraint(self):
        result = trade(
            timestamp=1000,
            side='bid',
            price=100.0,
            size=100,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=0,
            order_history=self.order_history
        )
        if result['order_type'] == 'new':
            self.assertEqual(round(result['price'] * 100) % 1, 0)

    def test_spread_constraint(self):
        result = trade(
            timestamp=1000,
            side='bid',
            price=100.0,
            size=100,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=0,
            order_history=self.order_history
        )
        if result['order_type'] == 'new':
            self.assertTrue(result['price'] < 100.0)

    def test_order_count_constraint(self):
        self.order_history = {i: {
            'order_id': i,
            'timestamp': 500,
            'side': 'bid',
            'price': 99.0,
            'size': 10,
            'status': 'active'
        } for i in range(1, 101)}
        
        result = trade(
            timestamp=1000,
            side='bid',
            price=100.0,
            size=100,
            action='new',
            current_capital=self.initial_capital,
            current_inventory=0,
            order_history=self.order_history
        )
        self.assertEqual(result['order_type'], 'hold')

if __name__ == '__main__':
    unittest.main()