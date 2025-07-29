from collections import deque
from typing import List, Tuple, Callable, Set, Dict
from collections import defaultdict

def can_reach_quorum(
    network: List[Tuple[int, int]],
    transaction: str,
    source_validator: int,
    quorum_size: int,
    max_hops: int,
    byzantine_tolerance: int,
    validation_function: Callable[[str, int], bool]
) -> bool:
    """
    Determines if a sufficient quorum of validators can be reached within the specified constraints.
    
    Args:
        network: List of tuples representing directed edges between validators
        transaction: Transaction data to be validated
        source_validator: Starting validator ID
        quorum_size: Minimum number of validators required
        max_hops: Maximum number of hops allowed
        byzantine_tolerance: Maximum number of Byzantine validators that can be tolerated
        validation_function: Function that returns validation result for a validator
    
    Returns:
        bool: True if quorum can be reached, False otherwise
    """
    
    # Build adjacency list representation of the network
    graph = defaultdict(set)
    all_nodes = set()
    for u, v in network:
        graph[u].add(v)
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Validate source_validator exists in network
    if not network or source_validator not in all_nodes:
        return False
    
    # Initialize BFS data structures
    queue = deque([(source_validator, 0)])  # (node, hops)
    visited = {source_validator}
    
    # Track validation results
    validation_results = {}
    
    def get_validator_result(validator_id: int) -> bool:
        """Cache validation results to avoid recomputing"""
        if validator_id not in validation_results:
            validation_results[validator_id] = validation_function(transaction, validator_id)
        return validation_results[validator_id]
    
    # Initial validation of source
    valid_validators = {source_validator} if get_validator_result(source_validator) else set()
    invalid_validators = {source_validator} if not get_validator_result(source_validator) else set()
    
    while queue:
        current_validator, hops = queue.popleft()
        
        if hops >= max_hops:
            continue
        
        # Process neighbors
        for neighbor in graph[current_validator]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, hops + 1))
                
                # Validate neighbor
                if get_validator_result(neighbor):
                    valid_validators.add(neighbor)
                else:
                    invalid_validators.add(neighbor)
                
                # Early success check
                if len(valid_validators) >= quorum_size:
                    # Check if we have enough valid validators even after
                    # accounting for potential Byzantine validators
                    remaining_valid = len(valid_validators) - byzantine_tolerance
                    if remaining_valid >= quorum_size:
                        return True
    
    # Final check considering Byzantine tolerance
    remaining_valid = len(valid_validators) - byzantine_tolerance
    return remaining_valid >= quorum_size
