import unittest
import threading
import time
from unittest.mock import patch, MagicMock, call

# Import the function under test from our service_availability module.
from service_availability import check_product_availability

class TestServiceAvailability(unittest.TestCase):
    @patch('service_availability.InventoryService')
    @patch('service_availability.PricingService')
    @patch('service_availability.PromotionService')
    def test_successful_availability(self, mock_promotion_service, mock_pricing_service, mock_inventory_service):
        # Setup: product is in stock.
        mock_inventory_service.checkAvailability.return_value = True
        # Pricing returns a base price.
        mock_pricing_service.getPrice.return_value = 100.0
        # Promotion service returns a list of promotions.
        mock_promotion_service.getPromotions.return_value = ["promoA", "promoB"]
        
        # Expected final price calculation (for test purposes assume each promotion deducts 10)
        expected_final_price = 100.0 - 10.0 * len(["promoA", "promoB"])
        expected_result = (True, expected_final_price, ["promoA", "promoB"])
        
        result = check_product_availability("prod_1")
        self.assertEqual(result, expected_result)
        
        # Verify that each service is called exactly once.
        mock_inventory_service.checkAvailability.assert_called_once_with("prod_1")
        mock_pricing_service.getPrice.assert_called_once_with("prod_1")
        mock_promotion_service.getPromotions.assert_called_once_with("prod_1")

    @patch('service_availability.InventoryService')
    @patch('service_availability.PricingService')
    @patch('service_availability.PromotionService')
    def test_product_not_available(self, mock_promotion_service, mock_pricing_service, mock_inventory_service):
        # Setup: product out of stock.
        mock_inventory_service.checkAvailability.return_value = False
        # Even if other services return values, they should not affect availability.
        mock_pricing_service.getPrice.return_value = 100.0
        mock_promotion_service.getPromotions.return_value = ["promoA"]
        
        # Expected behavior: if not in stock, return availability False, price 0.0 and empty promotions.
        expected_result = (False, 0.0, [])
        
        result = check_product_availability("prod_2")
        self.assertEqual(result, expected_result)
        
        mock_inventory_service.checkAvailability.assert_called_once_with("prod_2")
        # Pricing and promotion services might not be called if inventory fails.
        # We check that they are not called.
        mock_pricing_service.getPrice.assert_not_called()
        mock_promotion_service.getPromotions.assert_not_called()

    @patch('service_availability.InventoryService')
    @patch('service_availability.PricingService')
    @patch('service_availability.PromotionService')
    def test_retry_mechanism_on_pricing_failure(self, mock_promotion_service, mock_pricing_service, mock_inventory_service):
        # Setup: product is in stock.
        mock_inventory_service.checkAvailability.return_value = True
        
        # Simulate PricingService.getPrice failure in the first two calls and then success.
        pricing_side_effects = [Exception("Temporary failure"), Exception("Temporary failure"), 120.0]
        mock_pricing_service.getPrice.side_effect = pricing_side_effects
        
        # Promotion returns one promotion.
        mock_promotion_service.getPromotions.return_value = ["promoX"]
        
        # Expected final price: 120.0 minus 10 for each promotion.
        expected_final_price = 120.0 - 10.0 * len(["promoX"])
        expected_result = (True, expected_final_price, ["promoX"])
        
        result = check_product_availability("prod_3")
        self.assertEqual(result, expected_result)
        
        mock_inventory_service.checkAvailability.assert_called_once_with("prod_3")
        # Ensure getPrice was called three times due to retries.
        self.assertEqual(mock_pricing_service.getPrice.call_count, 3)
        mock_promotion_service.getPromotions.assert_called_once_with("prod_3")
    
    @patch('service_availability.InventoryService')
    @patch('service_availability.PricingService')
    @patch('service_availability.PromotionService')
    def test_caching_behavior(self, mock_promotion_service, mock_pricing_service, mock_inventory_service):
        # Setup for caching: all services return valid responses.
        mock_inventory_service.checkAvailability.return_value = True
        mock_pricing_service.getPrice.return_value = 150.0
        mock_promotion_service.getPromotions.return_value = ["promoY"]
        
        # Expected result.
        expected_final_price = 150.0 - 10.0 * len(["promoY"])
        expected_result = (True, expected_final_price, ["promoY"])
        
        # First call to cache the result.
        result1 = check_product_availability("prod_4")
        # Second call should hit the cache.
        result2 = check_product_availability("prod_4")
        
        self.assertEqual(result1, expected_result)
        self.assertEqual(result2, expected_result)
        
        # Assuming caching is implemented, the underlying services should have been called only once.
        mock_inventory_service.checkAvailability.assert_called_once_with("prod_4")
        mock_pricing_service.getPrice.assert_called_once_with("prod_4")
        mock_promotion_service.getPromotions.assert_called_once_with("prod_4")
    
    @patch('service_availability.InventoryService')
    @patch('service_availability.PricingService')
    @patch('service_availability.PromotionService')
    def test_concurrent_calls(self, mock_promotion_service, mock_pricing_service, mock_inventory_service):
        # Setup: product is in stock.
        mock_inventory_service.checkAvailability.return_value = True
        mock_pricing_service.getPrice.return_value = 200.0
        mock_promotion_service.getPromotions.return_value = ["promoZ"]
        
        expected_final_price = 200.0 - 10.0 * len(["promoZ"])
        expected_result = (True, expected_final_price, ["promoZ"])
        
        results = {}
        def worker(product_id, index):
            result = check_product_availability(product_id)
            results[index] = result
        
        threads = []
        num_threads = 10
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=("prod_5", i))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        for i in range(num_threads):
            self.assertEqual(results[i], expected_result)
        
        # If caching is implemented, underlying services called only once.
        mock_inventory_service.checkAvailability.assert_called_once_with("prod_5")
        mock_pricing_service.getPrice.assert_called_once_with("prod_5")
        mock_promotion_service.getPromotions.assert_called_once_with("prod_5")

if __name__ == '__main__':
    unittest.main()