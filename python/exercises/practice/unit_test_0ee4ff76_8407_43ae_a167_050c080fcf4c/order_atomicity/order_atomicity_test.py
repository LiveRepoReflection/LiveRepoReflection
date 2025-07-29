import unittest
from unittest.mock import patch
from order_atomicity import OrderOrchestrator

class OrderAtomicityTest(unittest.TestCase):
    def setUp(self):
        self.orchestrator = OrderOrchestrator()

    @patch('order_atomicity.NotificationService.send_notification', return_value=True)
    @patch('order_atomicity.ShippingService.cancel_shipment', return_value=True)
    @patch('order_atomicity.ShippingService.schedule_shipment', return_value="ship123")
    @patch('order_atomicity.PaymentService.refund', return_value=True)
    @patch('order_atomicity.PaymentService.charge', return_value="txn123")
    @patch('order_atomicity.InventoryService.release_stock', return_value=True)
    @patch('order_atomicity.InventoryService.reserve_stock', return_value=True)
    def test_successful_order(self, mock_reserve, mock_release, mock_charge, mock_refund, mock_schedule, mock_cancel, mock_notify):
        result = self.orchestrator.place_order(user_id=1, item_id=101, quantity=2, address="123 Main St")
        self.assertIsInstance(result, dict)
        self.assertIn("order_id", result)
        self.assertIn("transaction_id", result)
        self.assertIn("shipment_id", result)

    @patch('order_atomicity.InventoryService.reserve_stock', return_value=False)
    def test_inventory_failure(self, mock_reserve):
        result = self.orchestrator.place_order(user_id=1, item_id=101, quantity=2, address="123 Main St")
        self.assertIsInstance(result, str)
        self.assertIn("stock", result.lower())

    @patch('order_atomicity.PaymentService.charge', return_value=False)
    @patch('order_atomicity.InventoryService.release_stock', return_value=True)
    @patch('order_atomicity.InventoryService.reserve_stock', return_value=True)
    def test_payment_failure(self, mock_reserve, mock_release, mock_charge):
        result = self.orchestrator.place_order(user_id=2, item_id=202, quantity=1, address="456 Elm St")
        self.assertIsInstance(result, str)
        self.assertIn("payment", result.lower())

    @patch('order_atomicity.ShippingService.schedule_shipment', return_value=False)
    @patch('order_atomicity.PaymentService.refund', return_value=True)
    @patch('order_atomicity.PaymentService.charge', return_value="txn456")
    @patch('order_atomicity.InventoryService.release_stock', return_value=True)
    @patch('order_atomicity.InventoryService.reserve_stock', return_value=True)
    def test_shipping_failure(self, mock_reserve, mock_release, mock_charge, mock_refund, mock_schedule):
        result = self.orchestrator.place_order(user_id=3, item_id=303, quantity=3, address="789 Oak Ave")
        self.assertIsInstance(result, str)
        self.assertIn("shipping", result.lower())

    @patch('order_atomicity.NotificationService.send_notification', return_value=False)
    @patch('order_atomicity.ShippingService.cancel_shipment', return_value=True)
    @patch('order_atomicity.ShippingService.schedule_shipment', return_value="ship789")
    @patch('order_atomicity.PaymentService.refund', return_value=True)
    @patch('order_atomicity.PaymentService.charge', return_value="txn789")
    @patch('order_atomicity.InventoryService.release_stock', return_value=True)
    @patch('order_atomicity.InventoryService.reserve_stock', return_value=True)
    def test_notification_failure(self, mock_reserve, mock_release, mock_charge, mock_refund, mock_schedule, mock_cancel, mock_notify):
        result = self.orchestrator.place_order(user_id=4, item_id=404, quantity=4, address="101 Pine Rd")
        self.assertIsInstance(result, dict)
        self.assertIn("order_id", result)

if __name__ == '__main__':
    unittest.main()