import threading
import time
import random

# Global order store for idempotency and order state management.
# Stores order_id mapping to outcome (True for committed, False for cancelled)
ORDER_STORE = {}
ORDER_STORE_LOCK = threading.Lock()

# Maximum number of retry attempts for service calls.
MAX_RETRIES = 3
INITIAL_BACKOFF = 0.1

def retry_operation(func, *args, **kwargs):
    """Helper function to retry a service call with exponential backoff."""
    attempt = 0
    delay = INITIAL_BACKOFF
    while attempt < MAX_RETRIES:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            attempt += 1
            if attempt == MAX_RETRIES:
                raise e
            time.sleep(delay)
            delay *= 2
    # Should never reach here
    raise Exception("Operation failed after retries.")

class InventoryService:
    @staticmethod
    def reserve_inventory(items):
        # Simulate a delay for the service call.
        time.sleep(0.1)
        # 80% chance of successful reservation; otherwise, simulate a transient failure.
        if random.random() < 0.8:
            return True
        else:
            raise Exception("Inventory reservation failed")

    @staticmethod
    def commit_inventory(items):
        # Simulate committing inventory reservation.
        time.sleep(0.05)
        return True

    @staticmethod
    def release_inventory(items):
        # Simulate releasing the reserved inventory.
        time.sleep(0.05)
        return True

class PaymentService:
    @staticmethod
    def authorize_payment(payment_info):
        # Simulate a delay for payment authorization.
        time.sleep(0.1)
        # 85% chance to authorize payment; otherwise, simulate authorization failure.
        if random.random() < 0.85:
            return True
        else:
            return False

    @staticmethod
    def capture_payment(payment_info):
        # Simulate capturing payment.
        time.sleep(0.05)
        return True

    @staticmethod
    def void_payment(payment_info):
        # Simulate voiding the payment.
        time.sleep(0.05)
        return True

def validate_order(order):
    # Ensure required keys exist in the order object.
    required_keys = ["user_id", "order_id", "items", "payment_info"]
    for key in required_keys:
        if key not in order:
            raise ValueError(f"Missing required order field: {key}")
    # Additional validations can be performed here if needed.
    return True

def process_order(order):
    """
    Orchestrates the distributed transaction for processing an order.
    Returns True if the order is successfully processed (committed),
    or False if the order is rolled back.
    """
    # Validate order input.
    validate_order(order)
    order_id = order["order_id"]

    # Idempotency check: if order has been processed before, return the stored result.
    with ORDER_STORE_LOCK:
        if order_id in ORDER_STORE:
            return ORDER_STORE[order_id]
        # Mark order as pending.
        ORDER_STORE[order_id] = None

    try:
        # Step 1: Reserve inventory with retry mechanism.
        reserve_success = retry_operation(InventoryService.reserve_inventory, order["items"])
        if not reserve_success:
            raise Exception("Inventory reservation did not succeed.")

        # Step 2: Authorize payment with retry mechanism.
        payment_authorized = None
        attempt = 0
        delay = INITIAL_BACKOFF
        while attempt < MAX_RETRIES:
            payment_authorized = PaymentService.authorize_payment(order["payment_info"])
            if payment_authorized:
                break
            attempt += 1
            if attempt == MAX_RETRIES:
                break
            time.sleep(delay)
            delay *= 2

        if not payment_authorized:
            raise Exception("Payment authorization failed.")

        # Step 3: Capture payment.
        capture_result = PaymentService.capture_payment(order["payment_info"])
        if not capture_result:
            raise Exception("Payment capture failed.")

        # Step 4: Commit inventory reservation.
        commit_result = InventoryService.commit_inventory(order["items"])
        if not commit_result:
            raise Exception("Inventory commit failed.")

        # Order committed successfully.
        with ORDER_STORE_LOCK:
            ORDER_STORE[order_id] = True
        return True

    except Exception as e:
        # Compensation section: rollback all actions if any step fails.
        try:
            InventoryService.release_inventory(order["items"])
        except Exception:
            pass
        try:
            PaymentService.void_payment(order["payment_info"])
        except Exception:
            pass
        with ORDER_STORE_LOCK:
            ORDER_STORE[order_id] = False
        return False