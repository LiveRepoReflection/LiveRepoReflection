import unittest
from decimal import Decimal
from datetime import datetime, timedelta

class TestDEXReconciler(unittest.TestCase):
    def setUp(self):
        self.sample_snapshot1 = {
            'dex_id': 1,
            'timestamp': datetime.now(),
            'bids': [
                {'price': Decimal('1000.12345678'), 'quantity': Decimal('1.23456789')},
                {'price': Decimal('999.12345678'), 'quantity': Decimal('2.23456789')}
            ],
            'asks': [
                {'price': Decimal('1001.12345678'), 'quantity': Decimal('0.23456789')},
                {'price': Decimal('1002.12345678'), 'quantity': Decimal('3.23456789')}
            ]
        }

        self.sample_snapshot2 = {
            'dex_id': 2,
            'timestamp': datetime.now() + timedelta(seconds=1),
            'bids': [
                {'price': Decimal('1000.22345678'), 'quantity': Decimal('1.23456789')},
                {'price': Decimal('999.22345678'), 'quantity': Decimal('2.23456789')}
            ],
            'asks': [
                {'price': Decimal('1001.22345678'), 'quantity': Decimal('0.23456789')},
                {'price': Decimal('1002.22345678'), 'quantity': Decimal('3.23456789')}
            ]
        }

    def test_initialization(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2)
        self.assertIsNotNone(reconciler)

    def test_process_snapshot(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2)
        result = reconciler.process_snapshot(self.sample_snapshot1)
        self.assertTrue(result)

    def test_find_price_discrepancies(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2, price_threshold=Decimal('0.1'))
        reconciler.process_snapshot(self.sample_snapshot1)
        reconciler.process_snapshot(self.sample_snapshot2)
        discrepancies = reconciler.find_price_discrepancies()
        self.assertIsInstance(discrepancies, list)

    def test_find_quantity_discrepancies(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2, quantity_threshold=Decimal('0.1'))
        reconciler.process_snapshot(self.sample_snapshot1)
        reconciler.process_snapshot(self.sample_snapshot2)
        discrepancies = reconciler.find_quantity_discrepancies()
        self.assertIsInstance(discrepancies, list)

    def test_find_stale_orders(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2, stale_threshold=timedelta(seconds=5))
        reconciler.process_snapshot(self.sample_snapshot1)
        stale_orders = reconciler.find_stale_orders()
        self.assertIsInstance(stale_orders, list)

    def test_generate_report(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2)
        reconciler.process_snapshot(self.sample_snapshot1)
        reconciler.process_snapshot(self.sample_snapshot2)
        report = reconciler.generate_report()
        self.assertIsInstance(report, dict)
        self.assertIn('price_discrepancies', report)
        self.assertIn('quantity_discrepancies', report)
        self.assertIn('stale_orders', report)

    def test_invalid_dex_id(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2)
        invalid_snapshot = self.sample_snapshot1.copy()
        invalid_snapshot['dex_id'] = 3
        with self.assertRaises(ValueError):
            reconciler.process_snapshot(invalid_snapshot)

    def test_invalid_price_precision(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2)
        invalid_snapshot = self.sample_snapshot1.copy()
        invalid_snapshot['bids'][0]['price'] = Decimal('1000.123456789')
        with self.assertRaises(ValueError):
            reconciler.process_snapshot(invalid_snapshot)

    def test_invalid_quantity_precision(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=2)
        invalid_snapshot = self.sample_snapshot1.copy()
        invalid_snapshot['bids'][0]['quantity'] = Decimal('1.123456789')
        with self.assertRaises(ValueError):
            reconciler.process_snapshot(invalid_snapshot)

    def test_large_scale_processing(self):
        from dex_reconciler import DEXReconciler
        reconciler = DEXReconciler(num_dexes=100)
        for i in range(100):
            snapshot = self.sample_snapshot1.copy()
            snapshot['dex_id'] = i + 1
            snapshot['timestamp'] = datetime.now() + timedelta(seconds=i)
            self.assertTrue(reconciler.process_snapshot(snapshot))

    def test_concurrent_processing(self):
        from dex_reconciler import DEXReconciler
        import threading
        reconciler = DEXReconciler(num_dexes=2)
        
        def process_snapshot():
            snapshot = self.sample_snapshot1.copy()
            reconciler.process_snapshot(snapshot)

        threads = [threading.Thread(target=process_snapshot) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        report = reconciler.generate_report()
        self.assertIsInstance(report, dict)

    def test_memory_usage(self):
        import psutil
        import os
        from dex_reconciler import DEXReconciler
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        reconciler = DEXReconciler(num_dexes=100)
        for i in range(1000):
            snapshot = self.sample_snapshot1.copy()
            snapshot['dex_id'] = (i % 100) + 1
            snapshot['timestamp'] = datetime.now() + timedelta(seconds=i)
            reconciler.process_snapshot(snapshot)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        self.assertLess(memory_increase / 1024 / 1024, 100)  # Less than 100MB increase

if __name__ == '__main__':
    unittest.main()