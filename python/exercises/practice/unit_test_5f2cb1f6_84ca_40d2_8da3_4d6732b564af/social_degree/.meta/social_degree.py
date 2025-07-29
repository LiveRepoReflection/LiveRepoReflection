from collections import deque
import time


def calculate_k_degree_centrality(user_id, k, get_neighbors):
    """
    Calculate the k-degree centrality of a user in a decentralized social graph.
    
    Args:
        user_id: The ID of the user to analyze
        k: The maximum number of hops to consider (1 <= k <= 10)
        get_neighbors: Function that returns a generator of neighbor IDs for a given user
    
    Returns:
        int: The k-degree centrality (number of unique users reachable within k hops)
    
    Raises:
        ValueError: If k is less than 1 or greater than 10
    """
    # Validate k
    if k < 1 or k > 10:
        raise ValueError(f"k must be between 1 and 10 inclusive, got {k}")
    
    # Keep track of visited users to avoid cycles and duplicates
    visited = set([user_id])  # Include starting user to exclude from count
    
    # Queue for BFS: (user_id, current_hop)
    queue = deque([(user_id, 0)])
    
    # Track number of users found (excluding the starting user)
    unique_users_count = 0
    
    # Dictionary to cache neighbors for already processed user IDs
    neighbor_cache = {}
    
    # Process using BFS
    while queue:
        current_user, current_hop = queue.popleft()
        
        # Don't process further if we've reached the hop limit
        if current_hop >= k:
            continue
        
        # Check if neighbors are already cached
        if current_user in neighbor_cache:
            neighbors = neighbor_cache[current_user]
        else:
            # Get neighbors efficiently using the provided function
            # Convert generator to list to reuse it if needed
            neighbors = list(get_neighbors(current_user))
            neighbor_cache[current_user] = neighbors
        
        # Process each neighbor
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                unique_users_count += 1
                # Only add to queue if we haven't reached the maximum hop count
                if current_hop + 1 < k:
                    queue.append((neighbor, current_hop + 1))
    
    return unique_users_count


# Example usage (not part of the solution)
def example_usage():
    # Define a mock get_neighbors function for testing
    def mock_get_neighbors(user_id):
        graph = {
            1: [2, 3, 4],
            2: [1, 5],
            3: [1],
            4: [1],
            5: [2]
        }
        return iter(graph.get(user_id, []))
    
    # Calculate k-degree centrality for user 1 with k=2
    centrality = calculate_k_degree_centrality(1, 2, mock_get_neighbors)
    print(f"2-degree centrality for user 1: {centrality}")


if __name__ == "__main__":
    example_usage()