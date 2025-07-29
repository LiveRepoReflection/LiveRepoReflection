from collections import defaultdict, Counter
from typing import List, Set

def consensus(initial_values: List[int], adjacency_list: List[List[int]], f: int) -> int:
    # Input validation
    N = len(initial_values)
    if N == 0:
        raise ValueError("Empty input")
    if N != len(adjacency_list):
        raise ValueError("Mismatched lengths between values and adjacency list")
    if f >= N/3:
        raise ValueError("Too many Byzantine nodes")
    
    # Phase 1: Initialize the message storage
    round_values = defaultdict(lambda: defaultdict(set))
    for i in range(N):
        round_values[0][i].add(initial_values[i])
    
    # Run Byzantine agreement protocol for N-f rounds
    rounds_needed = N - f
    
    for round_num in range(rounds_needed):
        # Phase 2: Message broadcasting
        new_round_values = defaultdict(lambda: defaultdict(set))
        
        for node in range(N):
            # Each node broadcasts its values to its neighbors
            current_values = round_values[round_num][node]
            for neighbor in adjacency_list[node]:
                for value in current_values:
                    new_round_values[round_num + 1][neighbor].add(value)
        
        # Phase 3: Value filtering
        for node in range(N):
            values = new_round_values[round_num + 1][node]
            # Count frequency of each value
            value_counts = Counter(values)
            
            # Keep only values that appear more than f times
            filtered_values = {val for val, count in value_counts.items() if count > f}
            round_values[round_num + 1][node] = filtered_values
    
    # Phase 4: Decision making
    final_values = set()
    for node in range(N):
        final_values.update(round_values[rounds_needed - 1][node])
    
    # If multiple values remain, choose the smallest one
    # This ensures deterministic behavior
    if not final_values:
        # Fallback to initial values if no consensus reached
        return min(initial_values)
    
    return min(final_values)

def _validate_graph(adjacency_list: List[List[int]], N: int) -> bool:
    """Helper function to validate the graph structure"""
    if not all(isinstance(neighbors, list) for neighbors in adjacency_list):
        return False
    
    for i, neighbors in enumerate(adjacency_list):
        # Check that node doesn't connect to itself
        if i in neighbors:
            return False
        # Check that all neighbors are valid nodes
        if not all(0 <= n < N for n in neighbors):
            return False
        # Check for duplicate neighbors
        if len(set(neighbors)) != len(neighbors):
            return False
    
    return True