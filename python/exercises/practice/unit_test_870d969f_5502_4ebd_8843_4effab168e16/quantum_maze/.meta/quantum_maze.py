import heapq
from collections import defaultdict

def most_probable_path(N, edges, entangled_pairs, start, end):
    """
    Find the most probable path from start to end in a quantum maze.
    
    Args:
        N: Number of locations in the maze (numbered 0 to N-1).
        edges: List of tuples (u, v, p) representing directed edges from u to v with probability p.
        entangled_pairs: List of tuples (a, b, couplings) representing entangled pairs of locations.
        start: Starting location.
        end: Destination location.
        
    Returns:
        The probability of the most probable path from start to end.
    """
    # Build the graph representation
    graph = defaultdict(list)
    for u, v, p in edges:
        graph[u].append((v, p))
    
    # Create an entanglement lookup dictionary
    # For each node, find if it's in any entangled pair and what nodes it affects
    entanglement_map = {}
    for a, b, couplings in entangled_pairs:
        # When a is visited, it affects b
        if a not in entanglement_map:
            entanglement_map[a] = []
        entanglement_map[a].append((b, couplings))
        
    # Priority queue for Dijkstra's algorithm
    # We use negative log probabilities to turn this into a shortest path problem
    # (maximizing probability = minimizing negative log probability)
    # We store (neg_log_prob, node, visited_nodes) where visited_nodes tracks which nodes were visited
    # to handle entanglement effects properly
    pq = [(0, start, frozenset([start]))]
    
    # Best probabilities (in negative log form) to reach each node from specific visited sets
    best_probs = {}
    
    while pq:
        neg_log_prob, node, visited = heapq.heappop(pq)
        
        # If we've found a path to the end that's better than any previously found,
        # this is our answer (first path to end is most probable due to our priority queue)
        if node == end:
            return np.exp(-neg_log_prob)
        
        # Skip if we've already found a better path to this node with the same visited set
        if (node, visited) in best_probs and best_probs[(node, visited)] < neg_log_prob:
            continue
        
        # Apply entanglement effects if this node is in an entangled pair
        # We need to create a modified graph for the current exploration path
        current_graph = modify_graph_for_entanglement(graph.copy(), node, visited, entanglement_map)
        
        # Continue with standard Dijkstra algorithm using the modified graph
        for neighbor, prob in current_graph[node]:
            if prob <= 0:  # Skip impossible transitions
                continue
                
            new_neg_log_prob = neg_log_prob - np.log(prob)
            new_visited = visited.union([neighbor])
            
            # Update if we found a better path
            if (neighbor, new_visited) not in best_probs or new_neg_log_prob < best_probs[(neighbor, new_visited)]:
                best_probs[(neighbor, new_visited)] = new_neg_log_prob
                heapq.heappush(pq, (new_neg_log_prob, neighbor, new_visited))
    
    # If we've exhausted all possible paths and haven't reached the end,
    # there's no valid path
    return 0.0

def modify_graph_for_entanglement(graph, current_node, visited, entanglement_map):
    """
    Modifies the graph based on entanglement effects from visiting the current node.
    
    Args:
        graph: The original graph structure.
        current_node: The node currently being visited.
        visited: Set of nodes that have been visited.
        entanglement_map: Mapping of which nodes affect which other nodes.
        
    Returns:
        Modified graph with updated probabilities based on entanglement.
    """
    # Create a deep copy of the graph to avoid modifying the original
    modified_graph = defaultdict(list)
    for node, edges in graph.items():
        modified_graph[node] = edges.copy()
    
    # If the current node affects other nodes through entanglement
    if current_node in entanglement_map:
        for affected_node, couplings in entanglement_map[current_node]:
            # Only apply entanglement effects if the affected node has outgoing edges
            if affected_node in graph and graph[affected_node]:
                # Get the current edges from the affected node
                edges = modified_graph[affected_node]
                
                # Apply coupling factors to all relevant edges
                for i, (dest, prob) in enumerate(edges):
                    if dest in couplings:
                        # Multiply by the coupling factor
                        edges[i] = (dest, prob * couplings[dest])
                
                # Check if we need to normalize
                total_prob = sum(prob for _, prob in edges if prob > 0)
                if total_prob > 0:  # Only normalize if there are valid probabilities
                    modified_graph[affected_node] = [(dest, prob / total_prob if prob > 0 else 0) 
                                                     for dest, prob in edges]
                else:
                    # If all probabilities became 0 or negative, keep them at 0
                    modified_graph[affected_node] = [(dest, 0) for dest, _ in edges]
    
    return modified_graph

# Add numpy import for logarithm operations
import numpy as np