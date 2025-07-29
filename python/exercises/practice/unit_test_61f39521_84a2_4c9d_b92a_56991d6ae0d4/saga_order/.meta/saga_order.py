import random
import threading

# Global lock for simulating thread safety
lock = threading.Lock()

# Maximum number of retries for compensation functions
MAX_RETRIES = 3

def create_order(order_details):
    """Simulates creating an order. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def compensate_order(order_id):
    """Simulates compensating (cancelling) an order. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def reserve_inventory(order_details):
    """Simulates reserving inventory. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def compensate_inventory(order_details):
    """Simulates compensating inventory reservation. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def charge_payment(order_details):
    """Simulates charging the payment. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def compensate_payment(order_details):
    """Simulates compensating the payment. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def schedule_shipping(order_details):
    """Simulates scheduling shipping. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def compensate_shipping(order_details):
    """Simulates compensating shipping schedule. Might fail."""
    with lock:
        if random.random() < 0.8:
            return True
        else:
            return False

def attempt_compensation(comp_func, args, log, label):
    attempts = 0
    while attempts < MAX_RETRIES:
        result = comp_func(*args)
        if result:
            log.append(f"{label}: success")
            return True
        attempts += 1
    log.append(f"{label}: failure")
    return False

def orchestrate_transaction(order_details):
    log = []

    # Step 1: Create order
    if create_order(order_details):
        log.append("create_order: success")
    else:
        log.append("create_order: failure")
        return (False, log)

    # Step 2: Reserve inventory
    if reserve_inventory(order_details):
        log.append("reserve_inventory: success")
    else:
        log.append("reserve_inventory: failure")
        # Compensation: cancel created order
        attempt_compensation(compensate_order, (order_details["order_id"],), log, "compensate_order")
        return (False, log)

    # Step 3: Charge payment
    if charge_payment(order_details):
        log.append("charge_payment: success")
    else:
        log.append("charge_payment: failure")
        # Compensation in reverse order for previous successful steps
        attempt_compensation(compensate_inventory, (order_details,), log, "compensate_inventory")
        attempt_compensation(compensate_order, (order_details["order_id"],), log, "compensate_order")
        return (False, log)

    # Step 4: Schedule shipping
    if schedule_shipping(order_details):
        log.append("schedule_shipping: success")
        return (True, log)
    else:
        log.append("schedule_shipping: failure")
        # Compensation in reverse order: first for payment, then inventory, then order
        attempt_compensation(compensate_payment, (order_details,), log, "compensate_payment")
        attempt_compensation(compensate_inventory, (order_details,), log, "compensate_inventory")
        attempt_compensation(compensate_order, (order_details["order_id"],), log, "compensate_order")
        return (False, log)