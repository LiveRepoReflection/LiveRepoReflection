import random
import heapq
from collections import deque, defaultdict

def maximize_influence(graph, influence_scores, k, T, num_simulations):
    """
    Find the seed set of users to maximize the probability of activating at least T users.
    
    Args:
        graph: Dictionary representing the graph (adjacency list)
        influence_scores: Dictionary mapping user IDs to their influence scores
        k: Budget (number of users to initially activate)
        T: Target number of activated users
        num_simulations: Number of Monte Carlo simulations to run
    
    Returns:
        A sorted list of user IDs representing the optimal seed set
    """
    # Handle edge cases
    if not graph or not influence_scores:
        return []
    
    # If k is larger than the number of nodes, return all nodes
    if k >= len(graph):
        return sorted(graph.keys())
    
    # Use a greedy approach with Monte Carlo simulations
    seed_set = []
    remaining_nodes = set(graph.keys())
    
    for _ in range(k):
        if not remaining_nodes:
            break
        
        best_node = None
        best_probability = -1
        best_simulations = []
        
        for node in remaining_nodes:
            # Add this node to the seed set temporarily
            temp_seed_set = seed_set + [node]
            
            # Run simulations to estimate probability of reaching T users
            successful_simulations = []
            for sim in range(num_simulations):
                activated = run_simulation(graph, influence_scores, temp_seed_set)
                if len(activated) >= min(T, len(graph)):
                    successful_simulations.append(sim)
            
            probability = len(successful_simulations) / num_simulations
            
            # Update best node if this one has higher probability
            if probability > best_probability or \
               (probability == best_probability and sum(temp_seed_set) < sum(seed_set + [best_node])):
                best_node = node
                best_probability = probability
                best_simulations = successful_simulations
        
        # Add the best node to seed set and remove from candidates
        if best_node is not None:
            seed_set.append(best_node)
            remaining_nodes.remove(best_node)
    
    return sorted(seed_set)

def run_simulation(graph, influence_scores, seed_set):
    """
    Runs a single simulation of the influence propagation process.
    
    Args:
        graph: Dictionary representing the graph (adjacency list)
        influence_scores: Dictionary mapping user IDs to their influence scores
        seed_set: Initial set of activated users
    
    Returns:
        Set of all activated users after the process completes
    """
    # Initialize activated nodes with seed set
    activated = set(seed_set)
    
    # Use a queue for processing newly activated nodes
    queue = deque(seed_set)
    
    while queue:
        current_node = queue.popleft()
        
        # Try to activate each follower
        for follower in graph.get(current_node, []):
            if follower in activated:
                continue
            
            # Calculate activation probability
            current_influence = influence_scores.get(current_node, 0)
            follower_influence = influence_scores.get(follower, 0)
            
            # Handle edge case where both influences could be zero
            if current_influence == 0 and follower_influence == 0:
                probability = 0.5  # Default to 50% chance when both are zero
            elif follower_influence == 0:
                probability = 1.0  # Always activate if follower has no influence
            else:
                probability = current_influence / (current_influence + follower_influence)
            
            # Try to activate the follower
            if random.random() < probability:
                activated.add(follower)
                queue.append(follower)
    
    return activated

def maximize_influence_optimized(graph, influence_scores, k, T, num_simulations):
    """
    An optimized version of maximize_influence that uses more efficient data structures
    and sampling techniques for larger graphs.
    """
    if not graph or not influence_scores:
        return []
    
    if k >= len(graph):
        return sorted(graph.keys())
    
    # Instead of trying every node in each iteration, we can use a priority queue approach
    # with incremental evaluation of marginal gains
    seed_set = []
    remaining_nodes = set(graph.keys())
    
    # Pre-compute the expected spread for each node individually
    node_spreads = {}
    for node in remaining_nodes:
        successful_count = 0
        for _ in range(num_simulations):
            activated = run_simulation(graph, influence_scores, [node])
            if len(activated) >= min(T, len(graph)):
                successful_count += 1
        node_spreads[node] = successful_count / num_simulations
    
    # Use a priority queue to keep track of the best nodes
    # We use negative probability because heapq is a min-heap
    candidates = [(-prob, node) for node, prob in node_spreads.items()]
    heapq.heapify(candidates)
    
    # Greedily select k nodes
    for _ in range(k):
        if not candidates:
            break
        
        # Get the best candidate so far
        _, best_node = heapq.heappop(candidates)
        
        # Add to seed set
        seed_set.append(best_node)
        remaining_nodes.remove(best_node)
        
        # Reevaluate the candidates with updated seed set
        # For large graphs, we can skip this step and just use the initial estimates
        if len(graph) < 1000:
            candidates = []
            for node in remaining_nodes:
                temp_seed_set = seed_set + [node]
                successful_count = 0
                for _ in range(num_simulations):
                    activated = run_simulation(graph, influence_scores, temp_seed_set)
                    if len(activated) >= min(T, len(graph)):
                        successful_count += 1
                probability = successful_count / num_simulations
                candidates.append((-probability, node))
            heapq.heapify(candidates)
    
    return sorted(seed_set)

def run_simulation_efficient(graph, influence_scores, seed_set):
    """
    A more efficient version of the simulation that uses bitsets for large graphs.
    """
    # For small graphs, just use the regular simulation
    if len(graph) < 1000:
        return run_simulation(graph, influence_scores, seed_set)
    
    # For larger graphs, we can optimize using different data structures
    activated = set(seed_set)
    queue = deque(seed_set)
    
    # Pre-compute probabilities for edges to avoid recalculation
    edge_probabilities = {}
    for u in graph:
        u_influence = influence_scores.get(u, 0)
        for v in graph.get(u, []):
            v_influence = influence_scores.get(v, 0)
            if u_influence == 0 and v_influence == 0:
                edge_probabilities[(u, v)] = 0.5
            elif v_influence == 0:
                edge_probabilities[(u, v)] = 1.0
            else:
                edge_probabilities[(u, v)] = u_influence / (u_influence + v_influence)
    
    while queue:
        current_node = queue.popleft()
        
        for follower in graph.get(current_node, []):
            if follower in activated:
                continue
            
            # Use pre-computed probabilities
            probability = edge_probabilities.get((current_node, follower), 0)
            
            if random.random() < probability:
                activated.add(follower)
                queue.append(follower)
    
    return activated

def maximize_influence(graph, influence_scores, k, T, num_simulations):
    """
    Main function that selects between implementations based on graph size.
    """
    # For large graphs, use the optimized version
    if len(graph) > 1000:
        return maximize_influence_optimized(graph, influence_scores, k, T, num_simulations)
    
    # Handle edge cases
    if not graph or not influence_scores:
        return []
    
    # If k is larger than the number of nodes, return all nodes
    if k >= len(graph):
        return sorted(graph.keys())
    
    # Use a greedy approach with Monte Carlo simulations
    seed_set = []
    remaining_nodes = set(graph.keys())
    
    for _ in range(k):
        if not remaining_nodes:
            break
        
        best_node = None
        best_probability = -1
        
        for node in remaining_nodes:
            # Add this node to the seed set temporarily
            temp_seed_set = seed_set + [node]
            
            # Run simulations to estimate probability of reaching T users
            successful_count = 0
            for _ in range(num_simulations):
                activated = run_simulation(graph, influence_scores, temp_seed_set)
                if len(activated) >= min(T, len(graph)):
                    successful_count += 1
            
            probability = successful_count / num_simulations
            
            # Update best node if this one has higher probability
            if probability > best_probability or \
               (probability == best_probability and best_node is not None and 
                sum(temp_seed_set) < sum(seed_set + [best_node])):
                best_node = node
                best_probability = probability
        
        # Add the best node to seed set and remove from candidates
        if best_node is not None:
            seed_set.append(best_node)
            remaining_nodes.remove(best_node)
    
    return sorted(seed_set)