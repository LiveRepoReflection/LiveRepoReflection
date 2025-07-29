import math
import heapq

def optimize_network(network, requests, min_key_rate, node_capacity, amp_factor):
    """
    Optimize the QKD network by assigning an optimal path for each communication request 
    and compute the total distribution time. 
    If any request cannot be satisfied due to effective key rate below the threshold or 
    capacity constraints at any node, return None.
    
    Parameters:
    - network: dict; keys are node IDs, values are dicts of neighbor: loss_rate (float 0 to 1)
    - requests: list of tuples (source, destination, key_size)
    - min_key_rate: float; minimum acceptable effective key rate
    - node_capacity: int; capacity (bits/sec) that each node can handle
    - amp_factor: float; amplification factor at each relay (between 0 and 1)
    
    Returns:
    - (total_time, path_assignments) if all requests can be satisfied, 
      where total_time is sum of times for each request, and 
      path_assignments is a dictionary mapping request indices to the optimal path (list of nodes)
    - None if any request cannot be satisfied.
    """
    num_requests = len(requests)
    # To store resulting paths and effective rates for each request, keyed by request index
    path_assignments = {}
    effective_rates = {}   # effective_rates for each request
    total_time = 0.0

    # This dictionary tracks the total effective rate used at each node
    node_usage = {node: 0.0 for node in network.keys()}
    
    # Process each request individually.
    for req_index, (source, destination, key_size) in enumerate(requests):
        result = _find_optimal_path(source, destination, network, amp_factor)
        if result is None:
            return None
        eff_rate, path = result
        if eff_rate < min_key_rate:
            return None
        # Calculate distribution time for this request.
        request_time = key_size / eff_rate
        total_time += request_time
        path_assignments[req_index] = path
        effective_rates[req_index] = eff_rate
        # For each node in the path, accumulate the effective rate requirement.
        for node in path:
            node_usage[node] += eff_rate

    # Check node capacity constraints.
    for node, usage in node_usage.items():
        if usage > node_capacity:
            return None

    return (total_time, path_assignments)

def _find_optimal_path(source, destination, network, amp_factor):
    """
    Find the path from source to destination that maximizes the effective key rate.
    The effective key rate is computed as:
      effective_rate = (1-l1)*(amp_factor)*(1-l2)*...*(amp_factor)*(1-ln)
    where l1, l2, ..., ln are the channel loss rates along the path. Note that the amplification
    factor is applied at every relay node (i.e. for every edge except the final one).
    
    We solve this by maximizing log(effective_rate). For an edge from u to v with loss rate l:
      if v is the destination: add log(1-l)
      otherwise: add log(1-l) + log(amp_factor)
    
    Returns:
      (effective_rate, path) if a path exists,
      None if no path is found.
    """
    # Priority queue: items are (-current_log_rate, current_node, path_so_far)
    # We use negative log_rate because heapq is a min-heap but we want to maximize.
    heap = []
    # Start with source node; initial log rate is 0 since log(1) = 0.
    heapq.heappush(heap, (0.0, source, [source]))
    
    # best_logs[node] holds the best log effective rate found so far for that node.
    best_logs = {source: 0.0}

    while heap:
        # Because we are maximizing, current_log is stored (non-negative or negative?) Actually, we store log rates (<= 0)
        current_log, node, path = heapq.heappop(heap)
        # Since we stored values directly (not negated), and we are using min-heap, the smallest log means highest effective rate.
        # current_log is the accumulated log effective rate so far.
        # If node is destination, then we have reached a valid path.
        if node == destination:
            effective_rate = math.exp(current_log)
            return (effective_rate, path)
        # Explore neighbors.
        for neighbor, loss in network[node].items():
            # Check for valid edge: loss must be between 0 and 1.
            if loss < 0 or loss > 1:
                continue
            # Do not consider cycles that might reduce effective rate unnecessarily.
            if neighbor in path:
                continue

            # Determine additional log factor.
            if neighbor == destination:
                add_log = math.log(1 - loss)
            else:
                add_log = math.log(1 - loss) + math.log(amp_factor)
            new_log = current_log + add_log
            # If this new log is better than any previously recorded for neighbor, update.
            if neighbor not in best_logs or new_log > best_logs[neighbor]:
                best_logs[neighbor] = new_log
                new_path = path + [neighbor]
                heapq.heappush(heap, (new_log, neighbor, new_path))
    return None