import heapq
from collections import defaultdict, namedtuple

def optimal_routes(n, edges, source, destinations, alpha, beta):
    """
    Finds the optimal delivery routes from the source to each destination in the network.
    
    Args:
        n: Number of nodes in the graph
        edges: List of tuples (source_node, destination_node, cost, reliability)
        source: Source node ID
        destinations: List of destination node IDs
        alpha: Weighting factor for reliability
        beta: Weighting factor for cost
        
    Returns:
        Dictionary with destination node IDs as keys and optimal paths as values
    """
    # Build adjacency list representation of the graph
    graph = defaultdict(list)
    for src, dst, cost, reliability in edges:
        graph[src].append((dst, cost, reliability))
    
    # Initialize the result dictionary
    result = {dest: [] for dest in destinations}
    
    # Create a named tuple for storing the state in our priority queue
    State = namedtuple('State', ['neg_score', 'node', 'cost', 'reliability', 'path'])
    
    # For each destination, find the optimal path
    for destination in destinations:
        # Skip if source and destination are the same
        if source == destination:
            result[destination] = [source]
            continue
        
        # Use Dijkstra's algorithm with a custom scoring function
        visited = set()
        # Priority queue to store (neg_score, node, total_cost, total_reliability, path)
        # We use negative score because heapq is a min-heap and we want to maximize score
        pq = []
        
        # Initialize with the start node
        initial_state = State(0, source, 0, 1.0, [source])
        heapq.heappush(pq, initial_state)
        
        found = False
        
        while pq and not found:
            state = heapq.heappop(pq)
            neg_score, current, total_cost, total_reliability, path = state
            
            # Skip if we've already visited this node with a better score
            if current in visited:
                continue
            
            visited.add(current)
            
            # Check if we've reached the destination
            if current == destination:
                result[destination] = path
                found = True
                break
            
            # Explore neighbors
            for neighbor, edge_cost, edge_reliability in graph[current]:
                if neighbor not in visited:
                    new_cost = total_cost + edge_cost
                    new_reliability = total_reliability * edge_reliability
                    
                    # Calculate the score for this path
                    # Handle the case where alpha or beta could be 0
                    score_components = []
                    
                    if alpha > 0:
                        score_components.append(new_reliability ** alpha)
                    
                    if beta > 0:
                        # Avoid division by zero or very large numbers
                        if new_cost > 0:
                            score_components.append(1 / (new_cost ** beta))
                    
                    # If both alpha and beta are 0, just use path length as a tiebreaker
                    if not score_components:
                        new_score = -len(path) - 1  # Negative because shorter paths are better
                    else:
                        # Multiply all score components
                        new_score = 1
                        for component in score_components:
                            new_score *= component
                    
                    new_path = path + [neighbor]
                    
                    # Push to priority queue with negative score (for max-heap behavior)
                    new_state = State(-new_score, neighbor, new_cost, new_reliability, new_path)
                    heapq.heappush(pq, new_state)
    
    return result


# Alternative implementation for different algorithm choices
def optimal_routes_alternative(n, edges, source, destinations, alpha, beta):
    """
    Alternative implementation using a different approach.
    This uses a modified A* algorithm that calculates scores based on potential future paths.
    
    Args: same as optimal_routes
    Returns: same as optimal_routes
    """
    # Build adjacency list
    graph = defaultdict(list)
    for src, dst, cost, reliability in edges:
        graph[src].append((dst, cost, reliability))
    
    result = {dest: [] for dest in destinations}
    
    # For each destination, find the optimal path
    for destination in destinations:
        if source == destination:
            result[destination] = [source]
            continue
        
        # Store best score and path for each node
        best_scores = {}
        best_paths = {}
        
        # Priority queue of (neg_score, node, path, total_cost, total_reliability)
        pq = [(0, source, [source], 0, 1.0)]
        
        while pq:
            neg_score, current, path, total_cost, total_reliability = heapq.heappop(pq)
            
            # If we've found a better path to this node already, skip
            if current in best_scores and -neg_score <= best_scores[current]:
                continue
            
            # Record this as the best path to the current node
            best_scores[current] = -neg_score
            best_paths[current] = path
            
            # If we've reached the destination, we're done
            if current == destination:
                result[destination] = path
                break
            
            # Explore neighbors
            for neighbor, edge_cost, edge_reliability in graph[current]:
                new_cost = total_cost + edge_cost
                new_reliability = total_reliability * edge_reliability
                
                # Calculate score
                if alpha == 0 and beta == 0:
                    new_score = -len(path) - 1  # Use path length as tiebreaker
                else:
                    numerator = 1 if alpha == 0 else new_reliability ** alpha
                    denominator = 1 if beta == 0 else new_cost ** beta
                    new_score = numerator / denominator
                
                new_path = path + [neighbor]
                
                # Only consider this path if it's better than any we've seen to this node
                if neighbor not in best_scores or new_score > best_scores[neighbor]:
                    heapq.heappush(pq, (-new_score, neighbor, new_path, new_cost, new_reliability))
    
    return result