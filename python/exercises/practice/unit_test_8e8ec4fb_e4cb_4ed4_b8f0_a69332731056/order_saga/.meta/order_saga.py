import time
import random
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class OrderItem:
    item_id: str
    quantity: int

@dataclass
class OrderRequest:
    order_id: str
    user_id: int
    items: List[OrderItem]
    payment_info: Dict
    shipping_address: Dict

class InventoryService:
    @staticmethod
    def reserve_items(order_id: str, items: List[OrderItem]) -> Dict:
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.1:
            return {'status': 'failed', 'reason': 'timeout'}
        if random.random() < 0.05:
            return {'status': 'failed', 'reason': 'out_of_stock'}
        return {'status': 'success'}

    @staticmethod
    def release_items(order_id: str, items: List[OrderItem]) -> Dict:
        time.sleep(random.uniform(0.1, 0.3))
        return {'status': 'success'}

class PaymentService:
    @staticmethod
    def authorize_payment(order_id: str, user_id: int, amount: float, payment_info: Dict) -> Dict:
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.1:
            return {'status': 'failed', 'reason': 'timeout'}
        if random.random() < 0.05:
            return {'status': 'failed', 'reason': 'insufficient_funds'}
        return {'status': 'success'}

    @staticmethod
    def refund_payment(order_id: str, user_id: int, amount: float) -> Dict:
        time.sleep(random.uniform(0.1, 0.3))
        return {'status': 'success'}

class ShippingService:
    @staticmethod
    def prepare_shipment(order_id: str, user_id: int, items: List[OrderItem], address: Dict) -> Dict:
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.1:
            return {'status': 'failed', 'reason': 'timeout'}
        if random.random() < 0.05:
            return {'status': 'failed', 'reason': 'invalid_address'}
        return {'status': 'success'}

class OrderSaga:
    MAX_RETRIES = 3
    RETRY_DELAY = 0.5

    def __init__(self):
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.shipping_service = ShippingService()

    def process_order(self, order_data: Dict) -> str:
        order_request = OrderRequest(
            order_id=order_data['order_id'],
            user_id=order_data['user_id'],
            items=[OrderItem(**item) for item in order_data['items']],
            payment_info=order_data['payment_info'],
            shipping_address=order_data['shipping_address']
        )
        
        try:
            inventory_result = self._retry(
                lambda: self.inventory_service.reserve_items(
                    order_request.order_id,
                    order_request.items
                )
            )
            if inventory_result['status'] != 'success':
                return f"Order {order_request.order_id} failed"

            payment_result = self._retry(
                lambda: self.payment_service.authorize_payment(
                    order_request.order_id,
                    order_request.user_id,
                    self._calculate_total(order_request.items),
                    order_request.payment_info
                )
            )
            if payment_result['status'] != 'success':
                self.inventory_service.release_items(
                    order_request.order_id,
                    order_request.items
                )
                return f"Order {order_request.order_id} failed"

            shipping_result = self._retry(
                lambda: self.shipping_service.prepare_shipment(
                    order_request.order_id,
                    order_request.user_id,
                    order_request.items,
                    order_request.shipping_address
                )
            )
            if shipping_result['status'] != 'success':
                self.payment_service.refund_payment(
                    order_request.order_id,
                    order_request.user_id,
                    self._calculate_total(order_request.items)
                )
                self.inventory_service.release_items(
                    order_request.order_id,
                    order_request.items
                )
                return f"Order {order_request.order_id} failed"

            return f"Order {order_request.order_id} confirmed"

        except Exception as e:
            return f"Order {order_request.order_id} failed"

    def _retry(self, operation):
        for attempt in range(self.MAX_RETRIES):
            try:
                result = operation()
                if result['status'] == 'success' or attempt == self.MAX_RETRIES - 1:
                    return result
                time.sleep(self.RETRY_DELAY * (attempt + 1))
            except Exception:
                if attempt == self.MAX_RETRIES - 1:
                    return {'status': 'failed', 'reason': 'max_retries_exceeded'}
                time.sleep(self.RETRY_DELAY * (attempt + 1))
        return {'status': 'failed', 'reason': 'max_retries_exceeded'}

    def _calculate_total(self, items: List[OrderItem]) -> float:
        return sum(10 * item.quantity for item in items)