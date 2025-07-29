import random
import heapq
import collections
from typing import Dict, Set, List, Tuple, Any

def find_influential_users(graph: Dict[int, Dict[int, float]], k: int, iterations: int) -> Set[int]:
    """
    Find the k most influential users in a social network.
    
    Args:
        graph: A dictionary representing the directed graph.
               Keys are user IDs, values are dictionaries mapping neighbor IDs to influence probabilities.
        k: Number of seed users to select.
        iterations: Number of Monte Carlo simulations to run for influence estimation.
    
    Returns:
        A set of k user IDs representing the most influential seed set.
    """
    # Handle edge cases
    if not graph:
        return set()
    
    # Ensure k is not larger than the number of nodes
    k = min(k, len(graph))
    
    # Clean the graph: remove invalid probabilities
    clean_graph = _clean_graph(graph)
    
    # Use a greedy algorithm with lazy evaluation for influence maximization
    return _greedy_influence_maximization(clean_graph, k, iterations)

def _clean_graph(graph: Dict[int, Dict[int, float]]) -> Dict[int, Dict[int, float]]:
    """
    Remove edges with invalid probabilities from the graph.
    Valid probabilities must be in the range [0.0, 1.0].
    """
    clean_graph = {}
    for node, neighbors in graph.items():
        clean_graph[node] = {}
        for neighbor, prob in neighbors.items():
            # Check if probability is valid
            try:
                prob_value = float(prob)
                if 0.0 <= prob_value <= 1.0:
                    clean_graph[node][neighbor] = prob_value
            except (ValueError, TypeError):
                # Skip invalid probabilities
                continue
    return clean_graph

def _greedy_influence_maximization(graph: Dict[int, Dict[int, float]], k: int, iterations: int) -> Set[int]:
    """
    Implements the greedy algorithm for influence maximization with lazy evaluation.
    
    The algorithm selects nodes one by one, each time choosing the node that provides
    the maximum marginal gain in influence spread when added to the current seed set.
    """
    if k == 0:
        return set()
    
    # If k equals the number of nodes, return all nodes
    if k >= len(graph):
        return set(graph.keys())
    
    seed_set = set()
    
    # Initially all nodes are candidates
    remaining_nodes = set(graph.keys())
    
    # Priority queue for lazy evaluation
    # (negative_marginal_gain, node_id, last_seed_set_size)
    node_heap = []
    
    # Keep track of the current influence of the seed set
    current_influence = 0
    
    for _ in range(k):
        # If we need to initialize the heap or update all nodes
        if not node_heap:
            for node in remaining_nodes:
                # Try this node as a seed
                temp_seed_set = seed_set.copy()
                temp_seed_set.add(node)
                
                # Estimate influence with Monte Carlo simulations
                influence = _estimate_influence(graph, temp_seed_set, iterations)
                marginal_gain = influence - current_influence
                
                # Add to heap (negate for max-heap)
                heapq.heappush(node_heap, (-marginal_gain, node, len(seed_set)))
        
        # Lazy evaluation: update nodes only when necessary
        while node_heap:
            neg_gain, node, last_size = heapq.heappop(node_heap)
            
            # If this evaluation was done before the last node was added to seed_set,
            # we need to recalculate the marginal gain
            if last_size < len(seed_set):
                if node not in remaining_nodes:
                    continue
                
                temp_seed_set = seed_set.copy()
                temp_seed_set.add(node)
                
                influence = _estimate_influence(graph, temp_seed_set, iterations)
                marginal_gain = influence - current_influence
                
                # Put back with updated values
                heapq.heappush(node_heap, (-marginal_gain, node, len(seed_set)))
            else:
                # This is the best node to add next
                seed_set.add(node)
                remaining_nodes.remove(node)
                
                # Update the current influence
                current_influence = _estimate_influence(graph, seed_set, iterations)
                break
        
        # If no more nodes provide positive marginal gain
        if not node_heap and len(seed_set) < k:
            # Add remaining nodes to reach k
            seed_set.update(list(remaining_nodes)[:k-len(seed_set)])
    
    return seed_set

def _estimate_influence(graph: Dict[int, Dict[int, float]], seed_set: Set[int], iterations: int) -> float:
    """
    Estimate the expected influence spread of a seed set using Monte Carlo simulations.
    
    Args:
        graph: The social network graph.
        seed_set: The set of seed nodes.
        iterations: Number of Monte Carlo simulations to run.
    
    Returns:
        The estimated expected number of influenced nodes.
    """
    total_influence = 0
    
    for _ in range(iterations):
        # Run a single simulation
        influenced = _simulate_cascade(graph, seed_set)
        total_influence += len(influenced)
    
    # Return the average influence
    return total_influence / iterations if iterations > 0 else 0

def _simulate_cascade(graph: Dict[int, Dict[int, float]], seed_set: Set[int]) -> Set[int]:
    """
    Simulate a single cascade of influence from the seed set according to the
    Independent Cascade model.
    
    Args:
        graph: The social network graph.
        seed_set: The set of seed nodes.
    
    Returns:
        The set of nodes influenced at the end of the cascade.
    """
    # Initially, only the seed nodes are influenced
    influenced = seed_set.copy()
    
    # Queue of newly influenced nodes that need to attempt to influence their neighbors
    queue = collections.deque(seed_set)
    
    # Keep track of attempted influences to avoid repeated attempts
    attempted_influences = set()
    
    while queue:
        node = queue.popleft()
        
        # Get the neighbors of this node
        for neighbor, prob in graph.get(node, {}).items():
            # Skip if the neighbor is already influenced or if we've already attempted
            # to influence this neighbor from this node
            edge = (node, neighbor)
            if neighbor in influenced or edge in attempted_influences:
                continue
            
            # Mark this influence attempt
            attempted_influences.add(edge)
            
            # Try to influence with the given probability
            if random.random() < prob:
                influenced.add(neighbor)
                queue.append(neighbor)
    
    return influenced

def _degree_centrality(graph: Dict[int, Dict[int, float]]) -> Dict[int, float]:
    """
    Calculate the degree centrality of each node.
    Used for initial heuristic ranking.
    """
    centrality = {}
    for node in graph:
        # Out-degree
        out_degree = len(graph.get(node, {}))
        # Weighted out-degree: consider edge probabilities
        weighted_out_degree = sum(graph.get(node, {}).values())
        
        # Combine both measures
        centrality[node] = out_degree + weighted_out_degree
    
    return centrality