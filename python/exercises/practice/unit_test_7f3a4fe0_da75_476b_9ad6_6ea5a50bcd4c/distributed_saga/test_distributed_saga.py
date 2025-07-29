import unittest
from unittest.mock import Mock, patch
from distributed_saga.distributed_saga import orchestrate_order
from distributed_saga.services import (
    InventoryService,
    PaymentService,
    OrderService,
    NotificationService,
    InventoryError,
    PaymentError,
    OrderError
)

class TestDistributedSaga(unittest.TestCase):
    def setUp(self):
        self.order_details = {
            'user_id': 123,
            'items': [{'item_id': 'A1', 'quantity': 2}],
            'total_amount': 20.00
        }
        self.inventory_service = Mock(spec=InventoryService)
        self.payment_service = Mock(spec=PaymentService)
        self.order_service = Mock(spec=OrderService)
        self.notification_service = Mock(spec=NotificationService)

    def test_successful_order_placement(self):
        self.inventory_service.reserve_inventory.return_value = None
        self.payment_service.process_payment.return_value = None
        self.order_service.create_order.return_value = None
        self.notification_service.send_confirmation.return_value = None

        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )

        self.assertTrue(result)
        self.inventory_service.reserve_inventory.assert_called_once()
        self.payment_service.process_payment.assert_called_once()
        self.order_service.create_order.assert_called_once()
        self.notification_service.send_confirmation.assert_called_once()

    def test_inventory_reservation_failure(self):
        self.inventory_service.reserve_inventory.side_effect = InventoryError("Out of stock")

        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )

        self.assertFalse(result)
        self.inventory_service.reserve_inventory.assert_called_once()
        self.payment_service.process_payment.assert_not_called()
        self.order_service.create_order.assert_not_called()
        self.notification_service.send_confirmation.assert_not_called()

    def test_payment_failure_after_inventory_reservation(self):
        self.inventory_service.reserve_inventory.return_value = None
        self.payment_service.process_payment.side_effect = PaymentError("Insufficient funds")

        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )

        self.assertFalse(result)
        self.inventory_service.reserve_inventory.assert_called_once()
        self.payment_service.process_payment.assert_called_once()
        self.inventory_service.release_inventory.assert_called_once()
        self.order_service.create_order.assert_not_called()
        self.notification_service.send_confirmation.assert_not_called()

    def test_order_creation_failure_after_payment(self):
        self.inventory_service.reserve_inventory.return_value = None
        self.payment_service.process_payment.return_value = None
        self.order_service.create_order.side_effect = OrderError("Database error")

        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )

        self.assertFalse(result)
        self.inventory_service.reserve_inventory.assert_called_once()
        self.payment_service.process_payment.assert_called_once()
        self.order_service.create_order.assert_called_once()
        self.payment_service.refund_payment.assert_called_once()
        self.inventory_service.release_inventory.assert_called_once()
        self.notification_service.send_confirmation.assert_not_called()

    def test_notification_failure_does_not_trigger_rollback(self):
        self.inventory_service.reserve_inventory.return_value = None
        self.payment_service.process_payment.return_value = None
        self.order_service.create_order.return_value = None
        self.notification_service.send_confirmation.side_effect = Exception("Email service down")

        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )

        self.assertTrue(result)
        self.inventory_service.reserve_inventory.assert_called_once()
        self.payment_service.process_payment.assert_called_once()
        self.order_service.create_order.assert_called_once()
        self.notification_service.send_confirmation.assert_called_once()
        self.payment_service.refund_payment.assert_not_called()
        self.inventory_service.release_inventory.assert_not_called()

    def test_idempotent_compensation(self):
        self.inventory_service.reserve_inventory.return_value = None
        self.payment_service.process_payment.return_value = None
        self.order_service.create_order.side_effect = OrderError("Database error")

        # First call - should trigger compensation
        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )
        self.assertFalse(result)

        # Second call with same order details - compensation should be idempotent
        result = orchestrate_order(
            self.order_details,
            self.inventory_service,
            self.payment_service,
            self.order_service,
            self.notification_service
        )
        self.assertFalse(result)

        # Verify compensation was called twice but with same effect
        self.assertEqual(self.payment_service.refund_payment.call_count, 2)
        self.assertEqual(self.inventory_service.release_inventory.call_count, 2)

if __name__ == '__main__':
    unittest.main()