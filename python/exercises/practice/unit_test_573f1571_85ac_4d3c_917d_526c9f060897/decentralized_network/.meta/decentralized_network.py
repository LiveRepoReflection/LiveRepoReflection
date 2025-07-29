from collections import defaultdict, deque
from typing import List, Set, Dict
import random


def get_local_view(node: int, friendships: List[Set[int]], depth: int) -> Set[int]:
    """
    Get the set of nodes visible from a given node up to specified depth.
    Uses BFS to explore the network up to the knowledge depth.
    """
    visible_nodes = {node}
    queue = deque([(node, 0)])
    visited = {node}

    while queue:
        current_node, current_depth = queue.popleft()
        
        if current_depth >= depth:
            continue

        for neighbor in friendships[current_node]:
            visible_nodes.add(neighbor)
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, current_depth + 1))

    return visible_nodes


def merge_components(components: List[Set[int]], node_a: int, node_b: int) -> None:
    """
    Merge two components containing node_a and node_b.
    """
    component_a = None
    component_b = None

    for component in components:
        if node_a in component:
            component_a = component
        if node_b in component:
            component_b = component
        if component_a and component_b:
            break

    if component_a is not component_b and component_a and component_b:
        component_a.update(component_b)
        components.remove(component_b)


def estimate_local_components(node: int, visible_nodes: Set[int], 
                           friendships: List[Set[int]]) -> List[Set[int]]:
    """
    Estimate connected components within the visible subset of the network from a node.
    """
    components = []
    unprocessed = visible_nodes.copy()

    while unprocessed:
        start_node = unprocessed.pop()
        current_component = {start_node}
        queue = deque([start_node])

        while queue:
            current = queue.popleft()
            neighbors = friendships[current] & visible_nodes
            
            for neighbor in neighbors:
                if neighbor in unprocessed:
                    current_component.add(neighbor)
                    unprocessed.remove(neighbor)
                    queue.append(neighbor)

        components.append(current_component)

    return components


def estimate_components(n: int, user_data: List[Dict], 
                      friendships: List[Set[int]], knowledge_depth: int) -> int:
    """
    Estimate the number of connected components in a decentralized network.
    
    Args:
        n: Number of users in the network
        user_data: List of dictionaries containing user information
        friendships: List of sets containing friend IDs for each user
        knowledge_depth: Maximum depth of network knowledge for each user

    Returns:
        Estimated number of connected components in the network
    """
    # Input validation
    if n <= 0:
        raise ValueError("Number of users must be positive")
    if len(friendships) != n:
        raise ValueError("Friendships list must match number of users")
    if knowledge_depth <= 0:
        raise ValueError("Knowledge depth must be positive")

    # Verify friendship consistency and symmetry
    for i in range(n):
        for friend in friendships[i]:
            if i not in friendships[friend]:
                friendships[friend].add(i)

    # Initialize global components tracking
    global_components = []
    processed_nodes = set()

    # Process nodes in random order to avoid bias
    nodes = list(range(n))
    random.shuffle(nodes)

    # First pass: construct initial components based on local views
    for node in nodes:
        if node in processed_nodes:
            continue

        # Get visible nodes from current node's perspective
        visible_nodes = get_local_view(node, friendships, knowledge_depth)
        
        # Get local components within visible nodes
        local_components = estimate_local_components(node, visible_nodes, friendships)

        # Update global components
        for local_component in local_components:
            should_merge = False
            merge_candidates = []

            for existing_component in global_components:
                if any(node in existing_component for node in local_component):
                    should_merge = True
                    merge_candidates.append(existing_component)

            if should_merge:
                # Merge with existing components
                merged_component = local_component.union(*merge_candidates)
                for candidate in merge_candidates:
                    global_components.remove(candidate)
                global_components.append(merged_component)
            else:
                # Create new component
                global_components.append(local_component)

        processed_nodes.update(visible_nodes)

    # Second pass: merge components based on friendships
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for friend in friendships[i]:
                for comp_idx, component in enumerate(global_components):
                    if i in component and friend not in component:
                        for other_comp in global_components[comp_idx+1:]:
                            if friend in other_comp:
                                component.update(other_comp)
                                global_components.remove(other_comp)
                                changed = True
                                break

    # Handle isolated nodes
    isolated_nodes = set(range(n)) - set().union(*global_components)
    for node in isolated_nodes:
        global_components.append({node})

    return len(global_components)