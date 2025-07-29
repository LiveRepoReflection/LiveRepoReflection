from collections import defaultdict, deque
import heapq


def optimize_transaction_order(adjacency_list, node_properties):
    """
    Optimize the execution order of a transaction DAG to minimize expected rollback costs.
    
    Args:
        adjacency_list: A dictionary mapping node IDs to lists of their adjacent nodes.
        node_properties: A dictionary mapping node IDs to dictionaries containing 
                        'service_id', 'success_probability', 'operation_cost', and 'rollback_cost'.
                        
    Returns:
        A list of node IDs representing the optimal execution order.
    """
    if not adjacency_list:
        return []
    
    # Create reverse edges for topological ordering
    reverse_edges = defaultdict(list)
    in_degree = defaultdict(int)
    
    for node, neighbors in adjacency_list.items():
        if node not in in_degree:
            in_degree[node] = 0
        for neighbor in neighbors:
            reverse_edges[neighbor].append(node)
            in_degree[neighbor] += 1
    
    # Identify all nodes with topological constraints
    all_nodes = set(node_properties.keys())
    
    # Calculate risk factors for nodes
    # Risk factor: A higher value means we'd prefer to execute this node earlier
    # due to its high success probability and/or high rollback cost
    risk_factors = {}
    for node in all_nodes:
        props = node_properties[node]
        # Node with high success probability should be executed earlier
        # Node with high rollback cost should be executed later
        # This is a heuristic to balance these conflicting objectives
        risk_factor = props['success_probability'] * (1 / max(1, props['rollback_cost']))
        risk_factors[node] = risk_factor
    
    # Modified Kahn's algorithm for topological sorting
    # We use a priority queue to select nodes with the best risk factor
    result = []
    no_incoming_edges = []
    
    # Initialize with nodes that have no incoming edges
    for node in all_nodes:
        if in_degree[node] == 0:
            # We use negative risk factor as heapq is a min-heap
            heapq.heappush(no_incoming_edges, (-risk_factors[node], node))
    
    while no_incoming_edges:
        _, node = heapq.heappop(no_incoming_edges)
        result.append(node)
        
        # Remove outgoing edges
        for neighbor in adjacency_list.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(no_incoming_edges, (-risk_factors[neighbor], neighbor))
    
    # Check if we have a valid topological sort
    if len(result) != len(all_nodes):
        raise ValueError("The input graph contains a cycle and cannot be topologically sorted")
    
    return result