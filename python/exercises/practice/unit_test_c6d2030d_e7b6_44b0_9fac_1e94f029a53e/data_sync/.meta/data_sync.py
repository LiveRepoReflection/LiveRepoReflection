from collections import defaultdict, deque
from heapq import heappush, heappop
import math

def optimize_sync(N, M, data_sources, network_latency, reliability, updates):
    # Initialize data structures to track latest values and their propagation status
    latest_values = defaultdict(dict)  # node -> {key: value}
    propagation_queue = []  # Priority queue for propagation tasks
    result = []  # Final sequence of propagations
    
    # Initialize latest known values from data sources
    for i, source in enumerate(data_sources):
        for key, value in source.items():
            latest_values[i][key] = value

    # Process updates in order
    for key, value, origin_node in updates:
        latest_values[origin_node][key] = value
        # Add initial propagation tasks from the origin node
        add_propagation_tasks(propagation_queue, origin_node, key, value, N, network_latency, reliability)

    # Process propagation queue until empty
    seen_propagations = set()  # To avoid duplicate propagations
    while propagation_queue:
        cost, src, dst, key, value = heappop(propagation_queue)
        
        # Skip if destination is unreliable or this propagation was already done
        if reliability[dst] == 0 or (src, dst, key, value) in seen_propagations:
            continue

        # Skip if destination already has the latest value
        if key in latest_values[dst] and latest_values[dst][key] == value:
            continue

        # Perform propagation
        latest_values[dst][key] = value
        result.append((src, dst, key, value))
        seen_propagations.add((src, dst, key, value))

        # Add new propagation tasks from the destination node
        add_propagation_tasks(propagation_queue, dst, key, value, N, network_latency, reliability)

    return result

def add_propagation_tasks(queue, src_node, key, value, N, network_latency, reliability):
    """Add new propagation tasks to the priority queue."""
    if reliability[src_node] == 0:
        return
        
    for dst in range(N):
        if dst == src_node or network_latency[src_node][dst] == float('inf'):
            continue
            
        # Calculate propagation cost considering both latency and reliability
        propagation_cost = network_latency[src_node][dst]
        if reliability[src_node] > 0:
            propagation_cost *= (1 / reliability[src_node])
        else:
            propagation_cost = float('inf')
            
        heappush(queue, (propagation_cost, src_node, dst, key, value))

def calculate_total_cost(propagation_sequence, network_latency, reliability):
    """Calculate the total cost of a propagation sequence."""
    total_cost = 0
    for src, dst, _, _ in propagation_sequence:
        if reliability[src] > 0:
            total_cost += network_latency[src][dst] * (1 / reliability[src])
    return total_cost