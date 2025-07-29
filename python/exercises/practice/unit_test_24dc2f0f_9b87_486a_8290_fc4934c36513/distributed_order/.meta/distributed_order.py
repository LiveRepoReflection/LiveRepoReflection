import threading
import time

# Global shared resources
inventory = {}  # item_id: quantity
payment_records = {}  # order_id: 'processed'
item_prices = {}  # item_id: price
blacklist_order_ids = set()  # order_ids causing payment failure
shipping_error_order_ids = set()  # order_ids causing shipping failure

# Additional globals for compensation idempotency
_reserved_inventory_orders = {}  # order_id: list of reserved items details
_shipping_scheduled_orders = set()  # order_ids for which shipping was scheduled
_refunded_payments = set()  # order_ids for which payment was refunded
_resent_notifications = set()  # order_ids for which notification has been re-sent

inventory_lock = threading.Lock()
payment_lock = threading.Lock()
shipping_lock = threading.Lock()
notification_lock = threading.Lock()


def reserve_inventory(order_id, items):
    with inventory_lock:
        # First, check if all items are available
        for item in items:
            item_id = item['item_id']
            quantity_needed = item['quantity']
            if inventory.get(item_id, 0) < quantity_needed:
                print(f"LOG: Not enough inventory for item {item_id}")
                return False
        # All items available, reserve them
        for item in items:
            item_id = item['item_id']
            quantity_needed = item['quantity']
            inventory[item_id] -= quantity_needed
        # Store the reservation for potential rollback
        _reserved_inventory_orders[order_id] = items.copy()
        print(f"LOG: Inventory reserved for order {order_id}")
        return True


def compensate_inventory_reservation(order_id, items):
    with inventory_lock:
        if order_id in _reserved_inventory_orders:
            reserved_items = _reserved_inventory_orders.pop(order_id)
            for item in reserved_items:
                item_id = item['item_id']
                quantity = item['quantity']
                inventory[item_id] += quantity
            print(f"LOG: Inventory compensation done for order {order_id}")
        else:
            print(f"LOG: No inventory reservation found for order {order_id} (idempotent call)")


def process_payment(order_id, user_id, payment_info, amount):
    with payment_lock:
        if order_id in blacklist_order_ids:
            print(f"LOG: Payment processing failed for order {order_id} due to blacklist")
            return False
        # Simulate payment processing
        payment_records[order_id] = 'processed'
        print(f"LOG: Payment processed for order {order_id} for amount {amount}")
        return True


def refund_payment(order_id, user_id, amount):
    with payment_lock:
        if order_id in _refunded_payments:
            print(f"LOG: Payment already refunded for order {order_id} (idempotent call)")
            return
        if order_id in payment_records:
            # Simulate refund by removing the record or marking refunded
            payment_records.pop(order_id)
            _refunded_payments.add(order_id)
            print(f"LOG: Payment of amount {amount} refunded for order {order_id}")
        else:
            print(f"LOG: No payment record found for order {order_id} during refund (idempotent call)")


def schedule_shipping(order_id, shipping_address):
    with shipping_lock:
        if order_id in shipping_error_order_ids:
            print(f"LOG: Shipping scheduling failed for order {order_id}")
            return False
        # Simulate scheduling the shipping
        _shipping_scheduled_orders.add(order_id)
        print(f"LOG: Shipping scheduled for order {order_id} to address {shipping_address}")
        return True


def cancel_shipping(order_id):
    with shipping_lock:
        if order_id in _shipping_scheduled_orders:
            _shipping_scheduled_orders.remove(order_id)
            print(f"LOG: Shipping canceled for order {order_id}")
        else:
            print(f"LOG: No shipping scheduled for order {order_id} during cancellation (idempotent call)")


def send_confirmation_notification(order_id, user_id):
    with notification_lock:
        # Simulate sending notification always succeeds
        print(f"LOG: Confirmation notification sent for order {order_id} to user {user_id}")
        return True


def resend_confirmation_notification(order_id, user_id):
    with notification_lock:
        if order_id in _resent_notifications:
            print(f"LOG: Notification already resent for order {order_id} (idempotent call)")
            return
        # Simulate delay before resending notification
        time.sleep(0.1)
        _resent_notifications.add(order_id)
        print(f"LOG: Confirmation notification resent for order {order_id} to user {user_id}")


def place_order(order_id, items, user_id, payment_info, shipping_address):
    total_amount = 0.0
    try:
        if not reserve_inventory(order_id, items):
            print(f"LOG: Order {order_id} failed during inventory reservation")
            return False

        # Calculate total amount from items using item_prices
        for item in items:
            price = item_prices.get(item['item_id'], 0.0)
            total_amount += price * item['quantity']

        if not process_payment(order_id, user_id, payment_info, total_amount):
            print(f"LOG: Order {order_id} failed during payment processing")
            compensate_inventory_reservation(order_id, items)
            return False

        if not schedule_shipping(order_id, shipping_address):
            print(f"LOG: Order {order_id} failed during shipping scheduling")
            refund_payment(order_id, user_id, total_amount)
            compensate_inventory_reservation(order_id, items)
            return False

        if not send_confirmation_notification(order_id, user_id):
            print(f"LOG: Order {order_id} failed during notification sending")
            cancel_shipping(order_id)
            refund_payment(order_id, user_id, total_amount)
            compensate_inventory_reservation(order_id, items)
            return False

        print(f"LOG: Order {order_id} placed successfully")
        return True
    except Exception as e:
        print(f"LOG: Exception occurred during order {order_id}: {e}")
        try:
            cancel_shipping(order_id)
        except Exception as ex:
            print(f"LOG: Exception during shipping cancellation for order {order_id}: {ex}")
        try:
            refund_payment(order_id, user_id, total_amount)
        except Exception as ex:
            print(f"LOG: Exception during refund for order {order_id}: {ex}")
        try:
            compensate_inventory_reservation(order_id, items)
        except Exception as ex:
            print(f"LOG: Exception during inventory compensation for order {order_id}: {ex}")
        return False