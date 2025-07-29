import networkx as nx
from typing import List, Dict, Optional, Tuple

def optimize_resource_allocation(
    nodes: List[Dict],
    edges: List[Dict],
    total_resources: int
) -> Optional[Dict[Tuple[int, int], float]]:
    """
    Optimizes resource allocation in a network flow problem.
    
    Args:
        nodes: List of node dictionaries with id, capacity, and demand
        edges: List of edge dictionaries with source, destination, capacity, and cost
        total_resources: Total resources available for allocation
        
    Returns:
        Dictionary mapping edges to optimal flows, or None if infeasible
    """
    # Validate input
    if not nodes or not edges:
        return None

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes with demand attributes
    total_demand = 0
    for node in nodes:
        G.add_node(node['id'], demand=-node['demand'], capacity=node['capacity'])
        total_demand += node['demand']

    # Check if total demand exceeds available resources
    if abs(total_demand) > total_resources:
        return None

    # Add edges with capacity and weight attributes
    for edge in edges:
        G.add_edge(
            edge['source'],
            edge['destination'],
            capacity=edge['capacity'],
            weight=edge['cost']
        )

    # Check if the problem is feasible
    try:
        # First check if the flow is possible without considering node capacities
        flow_dict = nx.min_cost_flow(G, demand='demand', capacity='capacity', weight='weight')
    except nx.NetworkXUnfeasible:
        return None

    # Now verify node capacity constraints
    for node in nodes:
        node_id = node['id']
        inflow = sum(flow_dict[u][node_id] for u in G.predecessors(node_id))
        outflow = sum(flow_dict[node_id][v] for v in G.successors(node_id))
        
        # For supply nodes (demand > 0), outflow should be <= capacity
        if node['demand'] > 0 and outflow > node['capacity']:
            return None
        
        # For demand nodes (demand < 0), inflow should be <= capacity
        if node['demand'] < 0 and inflow > node['capacity']:
            return None

    # Convert flow dictionary to the required format
    result = {}
    for u in flow_dict:
        for v in flow_dict[u]:
            if flow_dict[u][v] > 0:
                result[(u, v)] = flow_dict[u][v]

    return result