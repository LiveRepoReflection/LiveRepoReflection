def verify_signature(user_id, signature, public_keys):
    # Dummy verification: expect signature to be "valid"
    # In a real implementation, this would cryptographically check the signature against public_keys[user_id]
    if signature != "valid":
        return False
    return True

def allocate_bandwidth(transactions, total_bandwidth, credit_balances, public_keys, max_cap, current_timestamp):
    # Define acceptable time window (in seconds)
    TIME_WINDOW = 300

    # Dictionary to track latest nonce per user
    last_nonce = {}

    # First, validate transactions one by one.
    # Also, sum the total credits offered.
    total_offered = 0
    for tx in transactions:
        user = tx["user_id"]
        # Validate signature
        if not verify_signature(user, tx["signature"], public_keys):
            raise ValueError("Invalid signature")
        # Validate credit balance
        if user not in credit_balances or credit_balances[user] < tx["credits_offered"]:
            raise ValueError("Insufficient credits")
        # Validate nonce: it must be greater than any previously seen for this user
        if user in last_nonce and tx["nonce"] <= last_nonce[user]:
            raise ValueError("Invalid nonce")
        last_nonce[user] = tx["nonce"]
        # Validate timestamp: must be within current_timestamp ± TIME_WINDOW
        if not (current_timestamp - TIME_WINDOW <= tx["timestamp"] <= current_timestamp + TIME_WINDOW):
            raise ValueError("Invalid timestamp")
        total_offered += tx["credits_offered"]

    # In case no credits offered (should not happen normally but avoid division by zero)
    if total_offered <= 0:
        # Allocate zero bandwidth to everyone and return credit balances unchanged
        allocation = {tx["user_id"]: 0 for tx in transactions}
        return allocation, credit_balances

    # Calculate base allocation for each transaction.
    # Use the weighted fair queueing mechanism: each user's raw share is proportional to credits_offered.
    # Then clamp by the requested bandwidth and the maximum bandwidth per user (max_cap * total_bandwidth).
    allocations = {}
    base_allocations = {}
    max_allowed_dict = {}
    # Save details per user for later bonus redistribution.
    tx_data = {}  # key: user_id, value: dict with tx details and computed values
    for tx in transactions:
        user = tx["user_id"]
        credits = tx["credits_offered"]
        request_bw = tx["bandwidth_request"]
        # raw allocation based solely on credits proportion
        raw_alloc = (credits / total_offered) * total_bandwidth
        # maximum allowed due to cap
        max_allowed = max_cap * total_bandwidth
        max_allowed_dict[user] = max_allowed
        # Base allocation: if request is less than raw, then full request is given.
        base = raw_alloc
        if request_bw < base:
            base = request_bw
        if base > max_allowed:
            base = max_allowed
        base_allocations[user] = base
        tx_data[user] = {
            "credits_offered": credits,
            "bandwidth_request": request_bw,
            "raw_alloc": raw_alloc,
            "max_allowed": max_allowed
        }
        allocations[user] = base

    sum_base = sum(allocations.values())

    # Determine if any transaction was limited by the maximum cap.
    any_capped = any(allocations[user] >= max_allowed_dict[user] for user in allocations)

    # Distribute leftover bandwidth only if:
    # 1. The total base allocation is less than total_bandwidth.
    # 2. No transaction was limited by the max cap (i.e. no cap-induced allocation).
    # 3. There is at least one transaction that is not already request-limited.
    leftover = total_bandwidth - sum_base
    if leftover > 0 and not any_capped:
        # Eligible for bonus: only those transactions for which the base allocation is less than the full possible allocation
        # Full possible allocation is the minimum of (requested bandwidth, max_allowed)
        eligible = {}
        for user in allocations:
            full_possible = tx_data[user]["bandwidth_request"]
            if full_possible > max_allowed_dict[user]:
                full_possible = max_allowed_dict[user]
            gap = full_possible - allocations[user]
            if gap > 0:
                eligible[user] = gap

        total_gap = sum(eligible.values())
        if total_gap > 0:
            # Distribute the leftover proportionally to the gap available for each eligible transaction.
            for user in eligible:
                bonus = leftover * (eligible[user] / total_gap)
                # Ensure we do not exceed the gap.
                if bonus > eligible[user]:
                    bonus = eligible[user]
                allocations[user] += bonus
            # Recalculate sum (not used further, but for consistency)
            sum_alloc = sum(allocations.values())
            # Note: If leftover remains undistributed due to rounding, it is left unused.

    # Update credit balances: deduct credits based on the allocated bandwidth.
    # Deduct proportional to the ratio: (allocated / requested) * credits_offered.
    updated_credits = credit_balances.copy()
    for tx in transactions:
        user = tx["user_id"]
        request_bw = tx["bandwidth_request"]
        credits_offered = tx["credits_offered"]
        # Avoid division by zero
        if request_bw > 0:
            fraction = allocations[user] / request_bw
        else:
            fraction = 0
        deducted = credits_offered * fraction
        updated_credits[user] = updated_credits[user] - deducted

    # Round allocations to two decimals
    for user in allocations:
        allocations[user] = round(allocations[user], 2)
    for user in updated_credits:
        updated_credits[user] = round(updated_credits[user], 2)

    return allocations, updated_credits