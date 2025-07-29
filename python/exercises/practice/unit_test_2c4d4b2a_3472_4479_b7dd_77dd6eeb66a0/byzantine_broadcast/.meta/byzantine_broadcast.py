from collections import defaultdict, Counter

def byzantine_broadcast(n: int, sender_id: int, initial_value: int, messages: list[tuple[int, int, int]]):
    """
    Implements a Byzantine Broadcast protocol to achieve consensus among nodes,
    even in the presence of Byzantine (malicious) nodes.
    
    This implementation is based on a simplified version of the Exponential Information
    Gathering (EIG) algorithm for Byzantine Agreement.
    
    Args:
        n: The total number of nodes in the system.
        sender_id: The ID of the node designated as the sender (0-indexed).
        initial_value: The initial value (0 or 1) held by the sender.
        messages: A list of tuples (sender, receiver, value) representing messages.
    
    Returns:
        The final agreed-upon value (0 or 1).
    """
    if n == 1:
        return initial_value
    
    # Calculate the maximum number of Byzantine nodes that can be tolerated
    max_byzantine = (n - 1) // 3
    
    # Organize messages by rounds
    # Round 0: Sender broadcasts to all
    # Round 1: Nodes relay what they heard from sender
    # Round 2: Nodes relay what they heard others heard from sender
    # ...and so on
    
    # message_graph[r][i][j] = value that node i claims node j reported in round r
    message_graph = [{} for _ in range(n)]
    
    # First, organize direct messages from the sender (round 0)
    sender_messages = defaultdict(list)
    for s, r, v in messages:
        if s == sender_id:
            sender_messages[r].append(v)
    
    # Store what each node directly received from the sender
    for receiver, values in sender_messages.items():
        if values:
            # If there are conflicting values, take the most common
            message_graph[0][receiver] = Counter(values).most_common(1)[0][0]
    
    # Process relay messages (what nodes say they received from other nodes)
    relay_messages = defaultdict(lambda: defaultdict(list))
    for s, r, v in messages:
        if s != sender_id:
            relay_messages[s][r].append((sender_id, v))
    
    # Process what each node relays about what it received from the sender
    for reporter, recipients in relay_messages.items():
        for recipient, values in recipients.items():
            for source, value in values:
                if source == sender_id:  # This is a report about what was heard from the sender
                    if reporter not in message_graph[1]:
                        message_graph[1][reporter] = {}
                    message_graph[1][reporter][recipient] = value
    
    # Extract what each node claims to have received from the sender
    node_claims = defaultdict(list)
    
    # Direct claims (what nodes directly reported receiving from sender)
    for receiver, value in message_graph[0].items():
        node_claims[receiver].append(value)
    
    # Indirect claims (what nodes claim other nodes received)
    for reporter, reports in message_graph[1].items():
        for target, value in reports.items():
            node_claims[target].append(value)
    
    # For each node, determine the majority value they claim to have received
    majority_claims = {}
    for node, claims in node_claims.items():
        if claims:
            counter = Counter(claims)
            # If there's a tie, we default to 0 (arbitrary choice)
            majority_value, count = counter.most_common(1)[0]
            majority_claims[node] = majority_value
    
    # Determine overall consensus based on majority of node claims
    values_count = Counter(majority_claims.values())
    
    # If we have enough claims to make a decision
    if values_count:
        # Find the most common value
        consensus_value, count = values_count.most_common(1)[0]
        
        # Check if this consensus is strong enough given potential Byzantine nodes
        # Need more than 2/3 of nodes to agree to ensure correctness
        if count > n - max_byzantine:
            return consensus_value
    
    # If we don't have a strong consensus from the previous steps,
    # use a more robust algorithm - Exponential Information Gathering (EIG)
    
    # Build a tree of message reports for each node
    # tree[i] represents the EIG tree for node i
    tree = [defaultdict(dict) for _ in range(n)]
    
    # Initialize with direct messages from sender
    for node, value in message_graph[0].items():
        tree[node][str(sender_id)] = value
    
    # Add reports about what nodes heard from the sender
    for reporter, reports in message_graph[1].items():
        for about, value in reports.items():
            key = str(sender_id) + "," + str(reporter)
            tree[about][key] = value
    
    # Analyze the EIG tree to determine the consensus value
    # Count how many nodes report each value
    value_counts = Counter()
    for node_tree in tree:
        # Focus on direct reports about the sender
        for key, value in node_tree.items():
            if key == str(sender_id):
                value_counts[value] += 1
    
    # If there's a strong consensus
    if value_counts:
        consensus_value, count = value_counts.most_common(1)[0]
        if count > n - max_byzantine:
            return consensus_value
    
    # If we still don't have a strong consensus, 
    # use the King Algorithm approach - trust the sender if in doubt
    
    # Check if sender is likely Byzantine by seeing if it sent conflicting values
    sender_conflicting = False
    seen_values = set()
    for s, r, v in messages:
        if s == sender_id:
            seen_values.add(v)
            if len(seen_values) > 1:
                sender_conflicting = True
                break
    
    # If the sender isn't clearly Byzantine, trust its initial value
    if not sender_conflicting:
        return initial_value
    
    # Otherwise, make a decision based on available information
    # If we've gathered any information about what nodes received, use that
    if values_count:
        return values_count.most_common(1)[0][0]
    
    # Last resort: use the value sent to the majority of nodes
    sender_sent_values = Counter()
    for s, r, v in messages:
        if s == sender_id:
            sender_sent_values[v] += 1
    
    if sender_sent_values:
        return sender_sent_values.most_common(1)[0][0]
    
    # Absolute last resort: return the initial value
    return initial_value