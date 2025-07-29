import unittest
from unittest.mock import patch, MagicMock
from order_saga.order_saga import OrderSaga

class TestOrderSaga(unittest.TestCase):
    def setUp(self):
        self.saga = OrderSaga()
        self.order_data = {
            'order_id': 'test123',
            'user_id': 456,
            'items': [{'item_id': 'A', 'quantity': 2}],
            'payment_info': {'type': 'credit_card', 'number': '4111111111111111'},
            'shipping_address': {'street': '123 Main St'}
        }

    @patch('order_saga.order_saga.InventoryService.reserve_items')
    @patch('order_saga.order_saga.PaymentService.authorize_payment')
    @patch('order_saga.order_saga.ShippingService.prepare_shipment')
    def test_successful_order(self, mock_ship, mock_pay, mock_inv):
        mock_inv.return_value = {'status': 'success'}
        mock_pay.return_value = {'status': 'success'}
        mock_ship.return_value = {'status': 'success'}

        result = self.saga.process_order(self.order_data)
        self.assertEqual(result, "Order test123 confirmed")

    @patch('order_saga.order_saga.InventoryService.reserve_items')
    @patch('order_saga.order_saga.PaymentService.authorize_payment')
    @patch('order_saga.order_saga.ShippingService.prepare_shipment')
    def test_failed_inventory(self, mock_ship, mock_pay, mock_inv):
        mock_inv.return_value = {'status': 'failed', 'reason': 'out_of_stock'}
        mock_pay.return_value = {'status': 'success'}
        mock_ship.return_value = {'status': 'success'}

        result = self.saga.process_order(self.order_data)
        self.assertEqual(result, "Order test123 failed")

    @patch('order_saga.order_saga.InventoryService.reserve_items')
    @patch('order_saga.order_saga.PaymentService.authorize_payment')
    @patch('order_saga.order_saga.ShippingService.prepare_shipment')
    def test_retry_mechanism(self, mock_ship, mock_pay, mock_inv):
        mock_inv.side_effect = [
            {'status': 'failed', 'reason': 'timeout'},
            {'status': 'success'}
        ]
        mock_pay.return_value = {'status': 'success'}
        mock_ship.return_value = {'status': 'success'}

        result = self.saga.process_order(self.order_data)
        self.assertEqual(result, "Order test123 confirmed")

    @patch('order_saga.order_saga.InventoryService.reserve_items')
    @patch('order_saga.order_saga.PaymentService.authorize_payment')
    @patch('order_saga.order_saga.ShippingService.prepare_shipment')
    def test_compensation_flow(self, mock_ship, mock_pay, mock_inv):
        mock_inv.return_value = {'status': 'success'}
        mock_pay.return_value = {'status': 'success'}
        mock_ship.return_value = {'status': 'failed', 'reason': 'invalid_address'}

        with patch('order_saga.order_saga.PaymentService.refund_payment') as mock_refund, \
             patch('order_saga.order_saga.InventoryService.release_items') as mock_release:
            result = self.saga.process_order(self.order_data)
            self.assertEqual(result, "Order test123 failed")
            mock_refund.assert_called_once()
            mock_release.assert_called_once()

    def test_concurrent_orders(self):
        with patch('order_saga.order_saga.InventoryService.reserve_items') as mock_inv, \
             patch('order_saga.order_saga.PaymentService.authorize_payment') as mock_pay, \
             patch('order_saga.order_saga.ShippingService.prepare_shipment') as mock_ship:
            
            mock_inv.side_effect = [
                {'status': 'success'},
                {'status': 'success'}
            ]
            mock_pay.side_effect = [
                {'status': 'success'},
                {'status': 'success'}
            ]
            mock_ship.side_effect = [
                {'status': 'success'},
                {'status': 'success'}
            ]

            order1 = self.order_data.copy()
            order2 = self.order_data.copy()
            order2['order_id'] = 'test456'

            result1 = self.saga.process_order(order1)
            result2 = self.saga.process_order(order2)
            
            self.assertEqual(result1, "Order test123 confirmed")
            self.assertEqual(result2, "Order test456 confirmed")
            self.assertEqual(mock_inv.call_count, 2)
            self.assertEqual(mock_pay.call_count, 2)
            self.assertEqual(mock_ship.call_count, 2)

if __name__ == '__main__':
    unittest.main()