from collections import deque, defaultdict
from typing import Set, List, Dict, Callable, Any, Optional


def get_mutual_friends(user_id_1: str, user_id_2: str, dht_query_function: Callable[[str], Optional[Dict[str, Any]]]) -> Set[str]:
    """
    Find mutual friends between two users in a decentralized social network.
    
    Args:
        user_id_1: ID of the first user
        user_id_2: ID of the second user
        dht_query_function: Function to query the DHT for user data
        
    Returns:
        Set of user IDs representing mutual friends
    """
    # Query the DHT for both users
    user1_data = dht_query_function(user_id_1)
    user2_data = dht_query_function(user_id_2)
    
    # If either user doesn't exist, return empty set
    if not user1_data or not user2_data:
        return set()
    
    # Extract connection lists
    user1_connections = set(user1_data.get("connections", []))
    user2_connections = set(user2_data.get("connections", []))
    
    # Return the intersection of the two connection sets
    return user1_connections.intersection(user2_connections)


def find_shortest_path(start_user_id: str, end_user_id: str, dht_query_function: Callable[[str], Optional[Dict[str, Any]]]) -> List[str]:
    """
    Find the shortest path between two users in a decentralized social network.
    
    Args:
        start_user_id: ID of the starting user
        end_user_id: ID of the target user
        dht_query_function: Function to query the DHT for user data
        
    Returns:
        List of user IDs representing the shortest path, or empty list if no path exists
    """
    # If start and end are the same, return just that user
    if start_user_id == end_user_id:
        # Verify the user exists
        if not dht_query_function(start_user_id):
            return []
        return [start_user_id]
    
    # Use BFS to find the shortest path
    visited = {start_user_id}
    queue = deque([(start_user_id, [start_user_id])])
    
    while queue:
        current_user_id, path = queue.popleft()
        
        # Get the current user's data
        user_data = dht_query_function(current_user_id)
        if not user_data:
            continue
        
        # Check each connection
        for connection_id in user_data.get("connections", []):
            if connection_id == end_user_id:
                # Found the target user
                return path + [end_user_id]
            
            if connection_id not in visited:
                visited.add(connection_id)
                queue.append((connection_id, path + [connection_id]))
    
    # No path found
    return []


def detect_community(user_id: str, dht_query_function: Callable[[str], Optional[Dict[str, Any]]], threshold: int) -> Set[str]:
    """
    Detect a community around a given user in a decentralized social network.
    
    Args:
        user_id: ID of the starting user
        dht_query_function: Function to query the DHT for user data
        threshold: Minimum number of connections within the community
        
    Returns:
        Set of user IDs representing the community
    """
    # Check if the seed user exists
    seed_user_data = dht_query_function(user_id)
    if not seed_user_data:
        return set()
    
    # Initial exploration phase - collect potential community members
    potential_community = set([user_id])
    connection_graph = defaultdict(set)
    
    # Queue for BFS exploration, limited to 2 hops to avoid too many DHT queries
    exploration_queue = deque([(user_id, 0)])  # (user_id, hop_count)
    visited = {user_id}
    
    MAX_EXPLORATION_HOPS = 2
    
    while exploration_queue:
        current_user_id, hop_count = exploration_queue.popleft()
        
        # Get user data
        user_data = dht_query_function(current_user_id)
        if not user_data:
            continue
        
        connections = user_data.get("connections", [])
        
        # Add edges to the connection graph
        for connection_id in connections:
            connection_graph[current_user_id].add(connection_id)
            
            # For the first MAX_EXPLORATION_HOPS hops, add to potential community and queue
            if hop_count < MAX_EXPLORATION_HOPS:
                potential_community.add(connection_id)
                
                if connection_id not in visited:
                    visited.add(connection_id)
                    exploration_queue.append((connection_id, hop_count + 1))
    
    # Second phase: fetch data for all potential community members to build the full graph
    for member_id in list(potential_community):
        if member_id not in connection_graph:  # Only query if we haven't already
            user_data = dht_query_function(member_id)
            if user_data:
                connections = user_data.get("connections", [])
                # Only add edges to other potential community members to keep the graph focused
                for connection_id in connections:
                    if connection_id in potential_community:
                        connection_graph[member_id].add(connection_id)
    
    # Third phase: iteratively refine the community
    # Start with all potential members
    community = potential_community.copy()
    
    # Iteratively remove users with fewer than threshold connections within the community
    changes_made = True
    while changes_made:
        changes_made = False
        
        for member_id in list(community):
            # Count connections within the current community
            connections_in_community = sum(1 for connection_id in connection_graph[member_id] if connection_id in community)
            
            # If below threshold, remove from community
            if connections_in_community < threshold:
                community.remove(member_id)
                changes_made = True
    
    return community