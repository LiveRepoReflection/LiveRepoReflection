import random
from collections import defaultdict
from typing import Dict, Tuple, Callable

def max_flow_bfs(graph: Dict[str, Dict[str, Tuple[int, float]]], 
                node_capacities: Dict[str, int],
                source: str, 
                destination: str) -> int:
    """Calculate maximum flow using BFS (Edmonds-Karp algorithm)"""
    parent = {}
    max_flow = 0
    residual_graph = defaultdict(dict)
    
    # Build residual graph
    for u in graph:
        for v, (cap, _) in graph[u].items():
            residual_graph[u][v] = cap
            residual_graph[v][u] = 0
    
    while True:
        queue = [source]
        parent = {source: None}
        found_path = False
        
        while queue and not found_path:
            u = queue.pop(0)
            for v in residual_graph[u]:
                if v not in parent and residual_graph[u][v] > 0:
                    parent[v] = u
                    if v == destination:
                        found_path = True
                        break
                    queue.append(v)
        
        if not found_path:
            break
            
        path_flow = float('inf')
        v = destination
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual_graph[u][v])
            v = u
            
        v = destination
        while v != source:
            u = parent[v]
            residual_graph[u][v] -= path_flow
            residual_graph[v][u] += path_flow
            v = u
            
        max_flow += path_flow
        
        # Check node capacity constraints
        node_flows = defaultdict(int)
        for u in residual_graph:
            for v in residual_graph[u]:
                if residual_graph[u][v] < graph.get(u, {}).get(v, (0, 0))[0]:
                    node_flows[v] += (graph[u][v][0] - residual_graph[u][v])
        
        for node, flow in node_flows.items():
            if flow > node_capacities[node]:
                return max_flow - (flow - node_capacities[node])
                
    return max_flow

def monte_carlo_simulation(graph: Dict[str, Dict[str, Tuple[int, float]]],
                          node_capacities: Dict[str, int],
                          source: str,
                          destination: str,
                          required_throughput: int,
                          num_simulations: int = 1000) -> float:
    """Estimate probability of meeting throughput requirement"""
    successes = 0
    
    for _ in range(num_simulations):
        # Create failed graph
        failed_graph = defaultdict(dict)
        for u in graph:
            for v, (cap, fail_prob) in graph[u].items():
                if random.random() > fail_prob:  # Edge is operational
                    failed_graph[u][v] = (cap, fail_prob)
        
        # Calculate max flow in failed graph
        flow = max_flow_bfs(failed_graph, node_capacities, source, destination)
        if flow >= required_throughput:
            successes += 1
    
    return successes / num_simulations

def optimize_supply_chain(graph: Dict[str, Dict[str, Tuple[int, float]]],
                        node_capacities: Dict[str, int],
                        source: str,
                        destination: str,
                        required_throughput: int,
                        confidence_level: float,
                        node_upgrade_cost: Callable[[str, int], int]) -> Dict[str, int]:
    """Optimize supply chain to meet throughput with confidence"""
    if confidence_level <= 0 or confidence_level > 1:
        raise ValueError("Confidence level must be between 0 and 1")
    if required_throughput <= 0:
        raise ValueError("Throughput must be positive")
    
    # First check if current setup meets requirements
    current_prob = monte_carlo_simulation(graph, node_capacities, source, destination, required_throughput)
    if current_prob >= confidence_level:
        return {}
    
    # Need to upgrade - use greedy approach
    upgrades = defaultdict(int)
    nodes = list(node_capacities.keys())
    
    while True:
        best_node = None
        best_cost_benefit = float('inf')
        
        for node in nodes:
            # Try adding 1 capacity to this node
            temp_capacities = node_capacities.copy()
            temp_capacities[node] += upgrades[node] + 1
            
            # Estimate new probability
            new_prob = monte_carlo_simulation(graph, temp_capacities, source, destination, required_throughput)
            
            if new_prob > current_prob:
                cost = node_upgrade_cost(node, 1)
                cost_benefit = cost / (new_prob - current_prob)
                
                if cost_benefit < best_cost_benefit:
                    best_cost_benefit = cost_benefit
                    best_node = node
        
        if best_node is None:
            break
            
        upgrades[best_node] += 1
        node_capacities[best_node] += 1
        current_prob = monte_carlo_simulation(graph, node_capacities, source, destination, required_throughput)
        
        if current_prob >= confidence_level:
            break
    
    if current_prob >= confidence_level:
        return dict(upgrades)
    else:
        return {}