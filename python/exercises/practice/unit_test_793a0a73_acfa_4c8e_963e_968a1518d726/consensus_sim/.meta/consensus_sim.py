import random
import math

def simulate_consensus(N, K, B, w_self, w_received, R, T):
    # Validate inputs
    if not (isinstance(N, int) and N > 0):
        raise ValueError("N must be a positive integer")
    if not (isinstance(K, int) and K > 0):
        raise ValueError("K must be a positive integer")
    if not (isinstance(R, int) and R > 0):
        raise ValueError("R (number of rounds) must be a positive integer")
    if T < 0:
        raise ValueError("Threshold T must be non-negative")
    if not (0.0 <= B <= 1.0):
        raise ValueError("B must be between 0.0 and 1.0 inclusive")
    
    # Effective K: if K > N-1, then effectiveK is N-1. 
    effective_K = min(K, N - 1)
    if abs(w_self + effective_K * w_received - 1.0) > 1e-9:
        raise ValueError("The weights do not sum to 1.0 when accounting for effective K")
    
    # Initialize nodes: each node is a dictionary with keys "value" and "byzantine"
    nodes = []
    for i in range(N):
        node = {
            "value": random.randint(-100, 100),
            "byzantine": False
        }
        nodes.append(node)
    
    # Determine Byzantine nodes. Number is round(B * N)
    num_byzantine = int(round(B * N))
    indices = list(range(N))
    random.shuffle(indices)
    byzantine_indices = set(indices[:num_byzantine])
    for idx in byzantine_indices:
        nodes[idx]["byzantine"] = True

    # Simulate rounds
    for round_num in range(1, R + 1):
        # Prepare a list for new updated values
        new_values = [None] * N

        # For each node, simulate receiving exactly effective_K messages from randomly selected nodes
        for i in range(N):
            # select effective_K nodes (exclude self)
            possible_indices = list(range(N))
            possible_indices.remove(i)
            selected = random.sample(possible_indices, effective_K)
            # Gather messages from selected nodes.
            messages = []
            for j in selected:
                sender = nodes[j]
                # Byzantine strategy: send extreme value. Alternate based on round_num.
                if sender["byzantine"]:
                    # Alternate between 1000 and -1000 depending on round number
                    message_value = 1000 if round_num % 2 == 0 else -1000
                else:
                    message_value = sender["value"]
                messages.append(message_value)
            
            # Update rule: update own value based on weighted average.
            # All nodes (honest or Byzantine) update their internal value in the same way.
            current_value = nodes[i]["value"]
            weighted_sum = w_self * current_value + w_received * sum(messages)
            new_values[i] = weighted_sum

        # Update all node values
        for i in range(N):
            nodes[i]["value"] = new_values[i]

        # Calculate standard deviation of all node values
        values = [node["value"] for node in nodes]
        mean_val = sum(values) / N
        variance = sum((v - mean_val) ** 2 for v in values) / N
        stddev = math.sqrt(variance)
        if stddev < T:
            return round_num

    return -1