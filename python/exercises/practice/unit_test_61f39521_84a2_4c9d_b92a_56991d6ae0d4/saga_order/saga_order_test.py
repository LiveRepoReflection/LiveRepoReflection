import unittest
from unittest.mock import patch
import saga_order

class SagaOrderTest(unittest.TestCase):
    def setUp(self):
        self.order_details = {
            "order_id": "order123",
            "user_id": "user456",
            "items": [{"item_id": "itemA", "quantity": 2}, {"item_id": "itemB", "quantity": 1}],
            "payment_method": {"card_number": "1234567890", "expiry_date": "12/24"},
            "shipping_address": {"street": "123 Main St", "city": "Anytown", "zip": "12345"},
        }

    @patch('saga_order.create_order', return_value=True)
    @patch('saga_order.reserve_inventory', return_value=True)
    @patch('saga_order.charge_payment', return_value=True)
    @patch('saga_order.schedule_shipping', return_value=True)
    def test_all_services_success(self, mock_schedule_shipping, mock_charge_payment, mock_reserve_inventory, mock_create_order):
        success, log = saga_order.orchestrate_transaction(self.order_details)
        self.assertTrue(success)
        # Expected log should record successful execution of each service without any compensations.
        expected_logs = [
            "create_order: success",
            "reserve_inventory: success",
            "charge_payment: success",
            "schedule_shipping: success"
        ]
        for entry in expected_logs:
            self.assertIn(entry, log)

    @patch('saga_order.create_order', return_value=True)
    @patch('saga_order.reserve_inventory', return_value=False)
    @patch('saga_order.compensate_order', return_value=True)
    def test_failure_at_inventory(self, mock_compensate_order, mock_reserve_inventory, mock_create_order):
        success, log = saga_order.orchestrate_transaction(self.order_details)
        self.assertFalse(success)
        # create_order succeeded, reserve_inventory failed and then order compensation was performed.
        self.assertIn("create_order: success", log)
        self.assertIn("reserve_inventory: failure", log)
        self.assertIn("compensate_order: success", log)

    @patch('saga_order.create_order', return_value=True)
    @patch('saga_order.reserve_inventory', return_value=True)
    @patch('saga_order.charge_payment', return_value=False)
    @patch('saga_order.compensate_inventory', return_value=True)
    @patch('saga_order.compensate_order', return_value=True)
    def test_failure_at_payment(self, mock_compensate_order, mock_compensate_inventory, mock_charge_payment, mock_reserve_inventory, mock_create_order):
        success, log = saga_order.orchestrate_transaction(self.order_details)
        self.assertFalse(success)
        # create_order and reserve_inventory succeeded, charge_payment failed,
        # thus triggering compensation in reverse order.
        self.assertIn("create_order: success", log)
        self.assertIn("reserve_inventory: success", log)
        self.assertIn("charge_payment: failure", log)
        self.assertIn("compensate_inventory: success", log)
        self.assertIn("compensate_order: success", log)

    @patch('saga_order.create_order', return_value=True)
    @patch('saga_order.reserve_inventory', return_value=True)
    @patch('saga_order.charge_payment', return_value=True)
    @patch('saga_order.schedule_shipping', return_value=False)
    @patch('saga_order.compensate_payment', return_value=True)
    @patch('saga_order.compensate_inventory', return_value=True)
    @patch('saga_order.compensate_order', return_value=True)
    def test_failure_at_shipping(self, mock_compensate_order, mock_compensate_inventory, mock_compensate_payment, mock_schedule_shipping, mock_charge_payment, mock_reserve_inventory, mock_create_order):
        success, log = saga_order.orchestrate_transaction(self.order_details)
        self.assertFalse(success)
        # The transaction fails at scheduling shipping.
        self.assertIn("create_order: success", log)
        self.assertIn("reserve_inventory: success", log)
        self.assertIn("charge_payment: success", log)
        self.assertIn("schedule_shipping: failure", log)
        # Compensation should occur in reverse order: payment, inventory, then order.
        self.assertIn("compensate_payment: success", log)
        self.assertIn("compensate_inventory: success", log)
        self.assertIn("compensate_order: success", log)

    @patch('saga_order.create_order', return_value=True)
    @patch('saga_order.reserve_inventory', return_value=True)
    @patch('saga_order.charge_payment', return_value=True)
    @patch('saga_order.schedule_shipping', return_value=False)
    def test_compensation_retry_mechanism(self, mock_schedule_shipping, mock_charge_payment, mock_reserve_inventory, mock_create_order):
        # Simulate that the compensate_payment function fails twice and succeeds on the third attempt.
        call_sequence = [False, False, True]
        with patch('saga_order.compensate_payment', side_effect=call_sequence) as mock_compensate_payment, \
             patch('saga_order.compensate_inventory', return_value=True) as mock_compensate_inventory, \
             patch('saga_order.compensate_order', return_value=True) as mock_compensate_order:
            success, log = saga_order.orchestrate_transaction(self.order_details)
            self.assertFalse(success)
            self.assertEqual(mock_compensate_payment.call_count, 3)
            self.assertIn("compensate_payment: success", log)
            self.assertIn("compensate_inventory: success", log)
            self.assertIn("compensate_order: success", log)

if __name__ == '__main__':
    unittest.main()