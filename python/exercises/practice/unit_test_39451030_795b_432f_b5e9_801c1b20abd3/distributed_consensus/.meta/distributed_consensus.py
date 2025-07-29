from collections import Counter

def simulate_consensus(N, initial_values, crash_pattern, max_rounds):
    # Initialize the state of nodes:
    # current_values: stores the current value for each node.
    # active: stores if a node is active (True) or crashed (False).
    current_values = initial_values[:]
    active = [True] * N

    # Number of rounds to execute: max_rounds
    for r in range(max_rounds):
        # Apply crash pattern for current round if specified.
        # Nodes in crash_pattern for this round crash BEFORE proposing.
        if r < len(crash_pattern):
            for node in crash_pattern[r]:
                # Crash node if it is active.
                if active[node]:
                    active[node] = False

        # Collect proposals from all active nodes.
        proposals = {}
        for i in range(N):
            if active[i]:
                proposals[i] = current_values[i]

        # If there are no active nodes, break out.
        if not proposals:
            break

        # Compute aggregated proposals: count frequency of each proposed value.
        proposal_values = list(proposals.values())
        counter = Counter(proposal_values)
        # Determine if any value has a majority.
        total_proposals = len(proposal_values)
        majority_threshold = (total_proposals // 2) + 1
        majority_value = None
        for value, count in counter.items():
            if count >= majority_threshold:
                majority_value = value
                break

        # Determine new value for active nodes for this round.
        if majority_value is not None:
            new_value = majority_value
        else:
            new_value = min(proposal_values)

        # Update values for active nodes.
        for i in range(N):
            if active[i]:
                current_values[i] = new_value

        # Check for consensus: All active nodes have the same value.
        active_values = [current_values[i] for i in range(N) if active[i]]
        if active_values and all(val == active_values[0] for val in active_values):
            break

    return current_values