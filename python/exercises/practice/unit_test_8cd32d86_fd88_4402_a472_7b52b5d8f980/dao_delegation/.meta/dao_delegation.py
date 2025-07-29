import math

def aggregate_votes(token_balances, delegations, delegation_threshold, proposal_id):
    # Sanitize token balances: convert negative token values to 0.
    sanitized_balances = {}
    for account, tokens in token_balances.items():
        sanitized_balances[account] = tokens if tokens >= 0 else 0

    # Ensure every delegator is present in token balances with at least 0 tokens.
    for delegator in delegations:
        if delegator not in sanitized_balances:
            sanitized_balances[delegator] = 0
        # Note: We don't add delegatee if missing; such delegations will be ignored.

    # Adjust delegation_threshold: if negative, set to 0.
    delegation_threshold = delegation_threshold if delegation_threshold >= 0 else 0

    # Build a dictionary of valid delegations.
    # A delegation is valid if:
    # 1. It is not a self delegation.
    # 2. The delegatee exists in sanitized_balances.
    # 3. The delegator's token balance is >= delegation_threshold.
    # 4. The delegation chain (starting from the immediate delegatee) does not form a cycle.
    valid_delegations = {}
    for delegator, delegatee in delegations.items():
        if delegator == delegatee:
            continue
        if delegatee not in sanitized_balances:
            continue
        if sanitized_balances.get(delegator, 0) < delegation_threshold:
            continue

        # Check for cycles in the delegation chain.
        visited = set()
        current = delegatee
        chain_valid = True
        while current in delegations:
            if current in visited:
                chain_valid = False
                break
            visited.add(current)
            current = delegations[current]
        if chain_valid:
            valid_delegations[delegator] = delegatee

    # Initialize voting power with each account's base token balance.
    voting_power = {}
    for account, tokens in sanitized_balances.items():
        voting_power[account] = tokens

    # For each valid delegation, add the contribution of the delegator, computed as the integer part of the square root of its token balance, to the immediate delegatee.
    for delegator, delegatee in valid_delegations.items():
        contribution = int(math.sqrt(sanitized_balances.get(delegator, 0)))
        voting_power[delegatee] += contribution

    return voting_power