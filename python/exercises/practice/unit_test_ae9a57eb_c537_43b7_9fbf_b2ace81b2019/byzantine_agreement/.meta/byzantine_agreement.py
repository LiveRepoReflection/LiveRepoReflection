import random
from collections import Counter


def reach_consensus(N, leader, proposed_value, faulty_nodes, network):
    """
    Simulates the Byzantine Agreement protocol to reach consensus among nodes.
    
    Args:
        N: The total number of nodes in the network.
        leader: The ID of the leader node.
        proposed_value: The binary value (0 or 1) proposed by the leader.
        faulty_nodes: A set of node IDs that are faulty.
        network: A list of lists representing the adjacency list of the network.
        
    Returns:
        A dictionary mapping node IDs to their final decisions (0 or 1).
    """
    if N == 0:
        return {}
    
    # Phase 1: Leader proposes a value to all other nodes
    received_from_leader = {}
    
    for node_id in range(N):
        if node_id == leader:
            # Leader knows its own proposed value
            received_from_leader[node_id] = proposed_value
        else:
            if leader in faulty_nodes:
                # If the leader is faulty, it might send different values to different nodes
                received_from_leader[node_id] = random.choice([0, 1]) if node_id in network[leader] else None
            else:
                # If the leader is loyal, it sends the proposed value to all connected nodes
                received_from_leader[node_id] = proposed_value if node_id in network[leader] else None
    
    # Phase 2: Each node relays the value it received to all other nodes
    relayed_values = {node_id: {} for node_id in range(N)}
    
    for sender in range(N):
        value_to_relay = received_from_leader[sender]
        
        for receiver in network[sender]:
            if sender in faulty_nodes:
                # If the sender is faulty, it might relay different values or even not relay
                if random.random() < 0.8:  # 80% chance to relay a value
                    relayed_values[receiver][sender] = random.choice([0, 1])
                # else: no value relayed (implicitly)
            else:
                # If the sender is loyal, it relays what it received from the leader
                if value_to_relay is not None:
                    relayed_values[receiver][sender] = value_to_relay
    
    # Phase 3: Each node tallies the values it received and decides
    decisions = {}
    
    for node_id in range(N):
        if node_id in faulty_nodes:
            # Faulty nodes might decide arbitrarily
            decisions[node_id] = random.choice([0, 1])
        else:
            # Loyal nodes tally the values and pick the majority
            values = [received_from_leader[node_id]] if received_from_leader[node_id] is not None else []
            values.extend([v for v in relayed_values[node_id].values() if v is not None])
            
            if not values:
                # If no values were received, default to None
                decisions[node_id] = None
            else:
                # Take the majority value
                counter = Counter(values)
                decisions[node_id] = counter.most_common(1)[0][0]
    
    return decisions