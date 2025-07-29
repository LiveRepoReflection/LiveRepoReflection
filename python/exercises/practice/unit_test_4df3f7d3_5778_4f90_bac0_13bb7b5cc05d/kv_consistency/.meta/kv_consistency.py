def resolve_conflicts(versions):
    """
    Resolves conflicts between multiple versions of data using vector clocks.
    
    Args:
        versions: A list of tuples, where each tuple is (value, vector_clock)
                 Each vector_clock is a dictionary with node IDs as keys and counters as values.
    
    Returns:
        A tuple (value, vector_clock) representing the resolved version.
    """
    if len(versions) == 1:
        return versions[0]
    
    # Find dominant versions (if any)
    dominant_versions = []
    for i, (value_i, clock_i) in enumerate(versions):
        is_dominant = True
        for j, (_, clock_j) in enumerate(versions):
            if i == j:
                continue
            
            # Check if clock_i dominates clock_j
            if not _is_dominant(clock_i, clock_j):
                is_dominant = False
                break
                
        if is_dominant:
            dominant_versions.append((value_i, clock_i))
    
    # If there are dominant versions, return the one that would come first lexicographically
    if dominant_versions:
        return min(dominant_versions, key=lambda x: x[0])
    
    # If there are no dominant versions, merge them
    merged_value = min([v[0] for v in versions])
    merged_clock = {}
    for _, clock in versions:
        for node, counter in clock.items():
            merged_clock[node] = max(merged_clock.get(node, 0), counter)
    
    return (merged_value, merged_clock)

def _is_dominant(clock_a, clock_b):
    """
    Checks if clock_a dominates clock_b.
    
    Clock A dominates clock B if:
    1. For every node in B, A's counter is greater than or equal to B's counter.
    2. There is at least one node where A's counter is strictly greater than B's.
    
    Args:
        clock_a: A dictionary representing vector clock A
        clock_b: A dictionary representing vector clock B
        
    Returns:
        True if clock_a dominates clock_b, False otherwise.
    """
    has_greater = False
    
    # Check condition 1: Every node in B should have counter in A >= counter in B
    for node, counter_b in clock_b.items():
        counter_a = clock_a.get(node, 0)
        if counter_a < counter_b:
            return False
        if counter_a > counter_b:
            has_greater = True
    
    # Check if A has nodes that B doesn't have
    for node, counter_a in clock_a.items():
        if node not in clock_b and counter_a > 0:
            has_greater = True
            break
    
    # Check condition 2: At least one node in A should have counter > counter in B
    return has_greater