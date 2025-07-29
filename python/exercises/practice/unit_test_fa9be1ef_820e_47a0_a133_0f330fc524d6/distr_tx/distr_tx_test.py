import unittest
from unittest.mock import patch
import time
from distr_tx import TransactionOrchestrator

class TransactionOrchestratorTest(unittest.TestCase):
    def setUp(self):
        self.orchestrator = TransactionOrchestrator()
        self.order_data = {
            "customer_id": "user123",
            "items": [
                {"item_id": "productA", "quantity": 2},
                {"item_id": "productB", "quantity": 1}
            ],
            "payment_info": {
                "card_number": "XXXX-XXXX-XXXX-1234",
                "expiry_date": "12/24",
                "cvv": "123"
            }
        }

    @patch('distr_tx.TransactionOrchestrator._send_notification')
    @patch('distr_tx.TransactionOrchestrator._reserve_inventory')
    @patch('distr_tx.TransactionOrchestrator._process_payment')
    @patch('distr_tx.TransactionOrchestrator._create_order')
    def test_successful_transaction(self, mock_create_order, mock_process_payment, mock_reserve_inventory, mock_send_notification):
        mock_create_order.return_value = "order456"
        mock_process_payment.return_value = True
        mock_reserve_inventory.return_value = True
        mock_send_notification.return_value = True

        result = self.orchestrator.process_order(self.order_data)
        self.assertEqual(result.get("status"), "success")
        self.assertIn("order_id", result)

    @patch('distr_tx.TransactionOrchestrator._send_notification')
    @patch('distr_tx.TransactionOrchestrator._reserve_inventory')
    @patch('distr_tx.TransactionOrchestrator._process_payment')
    @patch('distr_tx.TransactionOrchestrator._create_order')
    def test_payment_failure(self, mock_create_order, mock_process_payment, mock_reserve_inventory, mock_send_notification):
        mock_create_order.return_value = "order456"
        mock_process_payment.side_effect = Exception("Insufficient funds")
        # Even if subsequent steps are configured, they should not be called after payment failure.
        mock_reserve_inventory.return_value = True
        mock_send_notification.return_value = True

        result = self.orchestrator.process_order(self.order_data)
        self.assertEqual(result.get("status"), "failure")
        self.assertEqual(result.get("error"), "Payment failed")
        self.assertIn("reason", result)

    @patch('distr_tx.TransactionOrchestrator._send_notification')
    @patch('distr_tx.TransactionOrchestrator._reserve_inventory')
    @patch('distr_tx.TransactionOrchestrator._process_payment')
    @patch('distr_tx.TransactionOrchestrator._create_order')
    def test_inventory_failure(self, mock_create_order, mock_process_payment, mock_reserve_inventory, mock_send_notification):
        mock_create_order.return_value = "order456"
        mock_process_payment.return_value = True
        mock_reserve_inventory.side_effect = Exception("Inventory error")
        mock_send_notification.return_value = True

        result = self.orchestrator.process_order(self.order_data)
        self.assertEqual(result.get("status"), "failure")
        self.assertEqual(result.get("error"), "Inventory reservation failed")
        self.assertIn("reason", result)

    @patch('distr_tx.TransactionOrchestrator._send_notification')
    @patch('distr_tx.TransactionOrchestrator._reserve_inventory')
    @patch('distr_tx.TransactionOrchestrator._process_payment')
    @patch('distr_tx.TransactionOrchestrator._create_order')
    def test_notification_failure(self, mock_create_order, mock_process_payment, mock_reserve_inventory, mock_send_notification):
        mock_create_order.return_value = "order456"
        mock_process_payment.return_value = True
        mock_reserve_inventory.return_value = True
        mock_send_notification.side_effect = Exception("SMTP error")

        result = self.orchestrator.process_order(self.order_data)
        self.assertEqual(result.get("status"), "failure")
        self.assertEqual(result.get("error"), "Notification failed")
        self.assertIn("reason", result)

    @patch('distr_tx.TransactionOrchestrator._send_notification')
    @patch('distr_tx.TransactionOrchestrator._reserve_inventory')
    @patch('distr_tx.TransactionOrchestrator._process_payment')
    @patch('distr_tx.TransactionOrchestrator._create_order')
    def test_timeout(self, mock_create_order, mock_process_payment, mock_reserve_inventory, mock_send_notification):
        mock_create_order.return_value = "order456"
        
        def delayed_payment(*args, **kwargs):
            time.sleep(6)
            return True
        
        mock_process_payment.side_effect = delayed_payment
        mock_reserve_inventory.return_value = True
        mock_send_notification.return_value = True

        result = self.orchestrator.process_order(self.order_data)
        self.assertEqual(result.get("status"), "failure")
        self.assertEqual(result.get("error"), "Timeout")

    @patch('distr_tx.TransactionOrchestrator._send_notification')
    @patch('distr_tx.TransactionOrchestrator._reserve_inventory')
    @patch('distr_tx.TransactionOrchestrator._process_payment')
    @patch('distr_tx.TransactionOrchestrator._create_order')
    def test_idempotent_retry(self, mock_create_order, mock_process_payment, mock_reserve_inventory, mock_send_notification):
        mock_create_order.return_value = "order456"
        mock_process_payment.return_value = True
        mock_reserve_inventory.return_value = True
        mock_send_notification.return_value = True

        # First transaction call
        result1 = self.orchestrator.process_order(self.order_data)
        # Second transaction call with the same order data should yield the same outcome
        result2 = self.orchestrator.process_order(self.order_data)
        
        self.assertEqual(result1, result2)

if __name__ == '__main__':
    unittest.main()