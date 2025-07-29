import heapq
from collections import defaultdict

def find_optimal_path(graph, source, destination):
    """
    Find the optimal path across a network based on the described criteria.
    
    Args:
        graph: A dictionary representing the network graph.
        source: The ID of the source server.
        destination: The ID of the destination server.
        
    Returns:
        A list of server IDs representing the optimal path, or None if no path exists.
    """
    # Handle the case where source equals destination
    if source == destination:
        return [source]
    
    # Initialize data structures for Dijkstra's algorithm variant
    # We're using negative scores because heapq is a min-heap but we want to maximize scores
    best_scores = defaultdict(lambda: float('-inf'))
    best_scores[source] = 0
    
    # Track the best path to each node
    best_paths = {source: [source]}
    
    # Priority queue for path exploration (negative score, hop count, current node)
    # Using hop count as a secondary priority for tie-breaking
    priority_queue = [(0, 0, source)]
    
    # Track visited nodes to handle cycles
    visited = set()
    
    while priority_queue:
        neg_score, hop_count, current = heapq.heappop(priority_queue)
        current_score = -neg_score
        
        # Skip if we've found a better path to this node already
        if current in visited or current_score < best_scores[current]:
            continue
        
        # If we've reached the destination, return the path
        if current == destination:
            return best_paths[current]
        
        visited.add(current)
        
        # Explore all neighbors
        if 'edges' not in graph[current]:
            continue
            
        for neighbor, (latency, risk) in graph[current]['edges'].items():
            # Skip if we've already visited this neighbor
            if neighbor in visited:
                continue
            
            # Calculate new score by considering path score formula
            # When calculating ProcessingPowerScore and SecurityLevelScore, we only include
            # intermediate servers (not source or destination)
            processing_power = 0
            security_level = 0
            
            if neighbor != destination:  # only add if not destination
                processing_power = graph[neighbor]['processing_power']
                security_level = graph[neighbor]['security_level']
            
            # Calculate the new score based on the formula
            # PathScore = ProcessingPowerScore + SecurityLevelScore - TotalLatency - TotalSecurityRisk
            new_score = current_score + processing_power + security_level - latency - risk
            
            # If this path is better than any previously found path to neighbor
            if new_score > best_scores[neighbor]:
                best_scores[neighbor] = new_score
                
                # Update the path to this neighbor
                best_paths[neighbor] = best_paths[current] + [neighbor]
                
                # Add to priority queue with negative score (for max-heap behavior)
                # and hop count for tie-breaking
                heapq.heappush(priority_queue, (-new_score, hop_count + 1, neighbor))
    
    # If we exhaust all possible paths without reaching the destination
    return None