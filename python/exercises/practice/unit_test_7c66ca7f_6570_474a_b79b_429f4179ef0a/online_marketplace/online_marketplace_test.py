import unittest
from online_marketplace import OnlineMarketplace

class TestOnlineMarketplace(unittest.TestCase):
    def setUp(self):
        self.marketplace = OnlineMarketplace()
        self.sample_assets = [
            (1, 100, ["color:blue", "rarity:common"]),
            (2, 500, ["color:red", "rarity:legendary"]),
            (3, 200, ["color:green", "type:sword"]),
            (4, 1000, ["color:blue", "rarity:legendary"]),
            (5, 50, ["color:red", "type:shield"])
        ]

    def test_add_and_search_single_asset(self):
        self.marketplace.add_asset(*self.sample_assets[0])
        results = self.marketplace.search("color:blue", "price", 10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 1)

    def test_bulk_load_and_search(self):
        self.marketplace.bulk_load(self.sample_assets)
        results = self.marketplace.search("color:blue", "price", 10)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], 1)
        self.assertEqual(results[1][0], 4)

    def test_search_multiple_filters(self):
        self.marketplace.bulk_load(self.sample_assets)
        results = self.marketplace.search("color:blue AND rarity:legendary", "price", 10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 4)

    def test_update_price(self):
        self.marketplace.add_asset(*self.sample_assets[0])
        self.marketplace.update_price(1, 150)
        results = self.marketplace.search("color:blue", "price", 10)
        self.assertEqual(results[0][1], 150)

    def test_remove_asset(self):
        self.marketplace.bulk_load(self.sample_assets)
        self.marketplace.remove_asset(4)
        results = self.marketplace.search("color:blue", "price", 10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 1)

    def test_search_empty_query(self):
        self.marketplace.bulk_load(self.sample_assets)
        results = self.marketplace.search("", "price", 10)
        self.assertEqual(len(results), 5)

    def test_search_limit(self):
        self.marketplace.bulk_load(self.sample_assets)
        results = self.marketplace.search("", "price", 3)
        self.assertEqual(len(results), 3)

    def test_search_sort_by_asset_id(self):
        self.marketplace.bulk_load(self.sample_assets)
        results = self.marketplace.search("", "asset_id", 10)
        self.assertEqual([r[0] for r in results], [1, 2, 3, 4, 5])

    def test_search_nonexistent_attribute(self):
        self.marketplace.bulk_load(self.sample_assets)
        results = self.marketplace.search("nonexistent:value", "price", 10)
        self.assertEqual(len(results), 0)

    def test_update_nonexistent_asset(self):
        with self.assertRaises(ValueError):
            self.marketplace.update_price(999, 100)

    def test_remove_nonexistent_asset(self):
        with self.assertRaises(ValueError):
            self.marketplace.remove_asset(999)

    def test_thread_safety(self):
        import threading
        self.marketplace.bulk_load(self.sample_assets)
        
        def worker():
            for i in range(6, 1006):
                self.marketplace.add_asset(i, i*10, [f"color:thread_{i%10}"])
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        results = self.marketplace.search("", "asset_id", 2000)
        self.assertEqual(len(results), 1005)

if __name__ == '__main__':
    unittest.main()