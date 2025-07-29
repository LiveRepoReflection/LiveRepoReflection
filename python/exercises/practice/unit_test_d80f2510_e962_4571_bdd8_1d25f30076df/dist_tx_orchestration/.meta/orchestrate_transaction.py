import time

MAX_RETRIES = 3
TIMEOUT = 10  # seconds

def simulate_service_operation(service, method, payload):
    """
    Simulate a service operation call.
    A delay is simulated using the 'delay' field in payload.
    If payload contains 'fail': True then the operation fails.
    """
    delay = payload.get("delay", 0)
    # If delay exceeds TIMEOUT, simulate a timeout by sleeping longer than allowed.
    if delay > TIMEOUT:
        time.sleep(TIMEOUT + 1)
        return False
    else:
        time.sleep(delay)
    # Check for a simulated failure
    if payload.get("fail", False):
        return False
    return True

def attempt_operation(service, method, payload):
    """
    Attempt to execute a service operation with retries.
    Returns True if succeeds within MAX_RETRIES, else False.
    """
    retries = 0
    while retries < MAX_RETRIES:
        start_time = time.time()
        result = simulate_service_operation(service, method, payload)
        elapsed = time.time() - start_time
        # If operation took more than TIMEOUT seconds, treat as failure.
        if elapsed > TIMEOUT:
            result = False
        if result:
            return True
        retries += 1
    return False

def attempt_compensation(service, method, payload):
    """
    Attempt to execute a compensation operation with retries.
    The compensation operation is defined by the method name prefixed with 'compensate_'.
    Returns True if succeeds within MAX_RETRIES, else False.
    """
    compensation_method = "compensate_" + method
    retries = 0
    while retries < MAX_RETRIES:
        start_time = time.time()
        result = simulate_service_operation(service, compensation_method, payload)
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT:
            result = False
        if result:
            return True
        retries += 1
    return False

def orchestrate_transaction(operations):
    """
    Orchestrate a distributed transaction using a Saga-like pattern.
    
    Parameters:
        operations: a list of tuples (service, method, payload) representing
                    the operations to be executed in sequence.
                    
    Returns:
        True if the transaction is successful (all operations succeed),
        False if any operation fails and compensations are triggered.
    """
    completed_operations = []
    for service, method, payload in operations:
        success = attempt_operation(service, method, payload)
        if success:
            # Store the completed operation for potential compensation.
            completed_operations.append((service, method, payload))
        else:
            # Operation failure: Rollback all previous operations in reverse order.
            for comp_service, comp_method, comp_payload in reversed(completed_operations):
                # Attempt compensation; if a compensation fails, retry as per requirements.
                attempt_compensation(comp_service, comp_method, comp_payload)
            return False
    # If all operations succeed, the transaction is successful.
    return True