import json
import heapq
from collections import defaultdict, deque
import random
import math
import copy

def deploy_microservices(input_data):
    """
    Determine an optimal deployment of microservices across servers to minimize total cost.
    
    Args:
        input_data: A dictionary containing microservices, servers, dependencies, and network latency information.
        
    Returns:
        A dictionary with a "deployment" key mapping microservices to servers.
    """
    # Extract data from input
    microservices = {ms["id"]: ms for ms in input_data["microservices"]}
    servers = {server["id"]: server for server in input_data["servers"]}
    dependencies = input_data["dependencies"]
    network_latency = input_data["network_latency"]
    
    # Create dependency graph and check for cycles
    dependency_graph = build_dependency_graph(dependencies)
    if has_cycle(dependency_graph):
        raise ValueError("Input contains cyclic dependencies, which are not allowed")
    
    # Calculate network latency between all pairs of servers
    latency_map = calculate_all_latencies(servers, network_latency)
    
    # Use simulated annealing to find a good deployment
    best_deployment = simulated_annealing(microservices, servers, dependency_graph, latency_map)
    
    return {"deployment": best_deployment}

def build_dependency_graph(dependencies):
    """
    Build a directed graph from the dependencies list.
    
    Args:
        dependencies: List of [source, target] pairs where source depends on target.
        
    Returns:
        A dictionary representing the graph, where keys are microservice IDs and values are
        lists of microservice IDs that they depend on.
    """
    graph = defaultdict(list)
    
    for source, target in dependencies:
        graph[source].append(target)
        # Make sure all nodes are in the graph
        if target not in graph:
            graph[target] = []
            
    return graph

def has_cycle(graph):
    """
    Check if the directed graph contains a cycle using DFS.
    
    Args:
        graph: A directed graph represented as an adjacency list.
        
    Returns:
        True if the graph contains a cycle, False otherwise.
    """
    visited = set()
    path = set()
    
    def dfs(node):
        if node in path:
            return True
        if node in visited:
            return False
            
        visited.add(node)
        path.add(node)
        
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
                
        path.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    
    return False

def calculate_all_latencies(servers, network_latency):
    """
    Calculate the latency between all pairs of servers using Floyd-Warshall algorithm.
    
    Args:
        servers: Dictionary mapping server IDs to server data.
        network_latency: List of [server1, server2, latency] triples.
        
    Returns:
        A dictionary mapping (server1_id, server2_id) to latency.
    """
    # Initialize latency map with infinity for all pairs
    latency_map = {}
    server_ids = list(servers.keys())
    
    for s1 in server_ids:
        for s2 in server_ids:
            if s1 == s2:
                latency_map[(s1, s2)] = 0
            else:
                latency_map[(s1, s2)] = float('inf')
    
    # Fill in known latencies
    for s1, s2, latency in network_latency:
        latency_map[(s1, s2)] = latency
        latency_map[(s2, s1)] = latency  # Undirected graph
    
    # Floyd-Warshall algorithm
    for k in server_ids:
        for i in server_ids:
            for j in server_ids:
                if latency_map[(i, j)] > latency_map[(i, k)] + latency_map[(k, j)]:
                    latency_map[(i, j)] = latency_map[(i, k)] + latency_map[(k, j)]
    
    return latency_map

def calculate_total_cost(deployment, microservices, servers, dependency_graph, latency_map):
    """
    Calculate the total cost of a deployment.
    
    Args:
        deployment: Dictionary mapping microservice IDs to server IDs.
        microservices: Dictionary mapping microservice IDs to microservice data.
        servers: Dictionary mapping server IDs to server data.
        dependency_graph: Dictionary representing the dependency graph.
        latency_map: Dictionary mapping (server1_id, server2_id) to latency.
        
    Returns:
        The total cost as a floating point number.
    """
    # Initialize total cost
    total_cost = 0
    
    # Calculate communication costs
    for source, targets in dependency_graph.items():
        source_server = deployment.get(source)
        if source_server is None:
            continue
            
        for target in targets:
            target_server = deployment.get(target)
            if target_server is None:
                continue
                
            # If they're on different servers, add communication cost
            if source_server != target_server:
                latency = latency_map.get((source_server, target_server), float('inf'))
                total_cost += latency
    
    # Calculate resource violation penalties
    server_usage = defaultdict(lambda: {"cpu": 0, "memory": 0, "bandwidth": 0})
    
    # Sum up resource usage for each server
    for ms_id, server_id in deployment.items():
        ms = microservices.get(ms_id)
        if ms is None:
            continue
            
        server_usage[server_id]["cpu"] += ms["cpu_requirement"]
        server_usage[server_id]["memory"] += ms["memory_requirement"]
        server_usage[server_id]["bandwidth"] += ms["bandwidth_requirement"]
    
    # Calculate penalties for resource violations
    for server_id, usage in server_usage.items():
        server = servers.get(server_id)
        if server is None:
            continue
            
        # CPU violation
        cpu_excess = max(0, usage["cpu"] - server["cpu_capacity"])
        total_cost += cpu_excess ** 2
        
        # Memory violation
        memory_excess = max(0, usage["memory"] - server.get("memory_capacity", server.get("memory_requirement", 0)))
        total_cost += memory_excess ** 2
        
        # Bandwidth violation
        bandwidth_excess = max(0, usage["bandwidth"] - server["bandwidth_capacity"])
        total_cost += bandwidth_excess ** 2
    
    return total_cost

def generate_initial_deployment(microservices, servers):
    """
    Generate an initial deployment of microservices to servers.
    
    Args:
        microservices: Dictionary mapping microservice IDs to microservice data.
        servers: Dictionary mapping server IDs to server data.
        
    Returns:
        A dictionary mapping microservice IDs to server IDs.
    """
    deployment = {}
    server_ids = list(servers.keys())
    
    # Simple greedy approach - assign each microservice to the server with most remaining capacity
    server_remaining = {
        server_id: {
            "cpu": server["cpu_capacity"],
            "memory": server.get("memory_capacity", server.get("memory_requirement", 0)),
            "bandwidth": server["bandwidth_capacity"]
        }
        for server_id, server in servers.items()
    }
    
    # Sort microservices by total resource requirements (descending)
    ms_sorted = sorted(
        microservices.keys(),
        key=lambda ms_id: (
            microservices[ms_id]["cpu_requirement"] + 
            microservices[ms_id]["memory_requirement"] + 
            microservices[ms_id]["bandwidth_requirement"]
        ),
        reverse=True
    )
    
    for ms_id in ms_sorted:
        ms = microservices[ms_id]
        
        # Find best server with sufficient capacity
        best_server_id = None
        best_server_fit = float('-inf')
        
        for server_id, remaining in server_remaining.items():
            # Calculate fit as the minimum remaining capacity after assignment
            cpu_fit = remaining["cpu"] - ms["cpu_requirement"]
            memory_fit = remaining["memory"] - ms["memory_requirement"]
            bandwidth_fit = remaining["bandwidth"] - ms["bandwidth_requirement"]
            
            fit_score = min(cpu_fit, memory_fit, bandwidth_fit)
            
            # Choose server with best fit (even if negative, as we have to place somewhere)
            if fit_score > best_server_fit:
                best_server_fit = fit_score
                best_server_id = server_id
        
        # If no server found (should not happen with our approach), pick a random one
        if best_server_id is None:
            best_server_id = random.choice(server_ids)
        
        # Assign microservice to best server
        deployment[ms_id] = best_server_id
        
        # Update remaining capacity
        server_remaining[best_server_id]["cpu"] -= ms["cpu_requirement"]
        server_remaining[best_server_id]["memory"] -= ms["memory_requirement"]
        server_remaining[best_server_id]["bandwidth"] -= ms["bandwidth_requirement"]
    
    return deployment

def get_neighbor_deployment(deployment, microservices, servers):
    """
    Generate a neighbor deployment by moving a random microservice to a random server.
    
    Args:
        deployment: Current deployment mapping microservice IDs to server IDs.
        microservices: Dictionary mapping microservice IDs to microservice data.
        servers: Dictionary mapping server IDs to server data.
        
    Returns:
        A new deployment dictionary.
    """
    new_deployment = deployment.copy()
    
    # Choose a random microservice
    ms_id = random.choice(list(deployment.keys()))
    current_server = deployment[ms_id]
    
    # Choose a random different server
    server_ids = list(servers.keys())
    if len(server_ids) > 1:
        new_server = current_server
        while new_server == current_server:
            new_server = random.choice(server_ids)
    else:
        # If only one server, we can't change anything
        return new_deployment
    
    # Move the microservice to the new server
    new_deployment[ms_id] = new_server
    
    return new_deployment

def simulated_annealing(microservices, servers, dependency_graph, latency_map):
    """
    Use simulated annealing to find a good deployment.
    
    Args:
        microservices: Dictionary mapping microservice IDs to microservice data.
        servers: Dictionary mapping server IDs to server data.
        dependency_graph: Dictionary representing the dependency graph.
        latency_map: Dictionary mapping (server1_id, server2_id) to latency.
        
    Returns:
        A deployment dictionary mapping microservice IDs to server IDs.
    """
    # Parameters for simulated annealing
    initial_temp = 100.0
    final_temp = 0.1
    cooling_rate = 0.95
    iterations_per_temp = 100
    
    # Initialize with a random deployment
    current_deployment = generate_initial_deployment(microservices, servers)
    current_cost = calculate_total_cost(current_deployment, microservices, servers, dependency_graph, latency_map)
    
    best_deployment = current_deployment.copy()
    best_cost = current_cost
    
    temp = initial_temp
    
    # Main simulated annealing loop
    while temp > final_temp:
        for _ in range(iterations_per_temp):
            # Generate a neighbor deployment
            neighbor_deployment = get_neighbor_deployment(current_deployment, microservices, servers)
            neighbor_cost = calculate_total_cost(neighbor_deployment, microservices, servers, dependency_graph, latency_map)
            
            # Determine if we should accept the new solution
            cost_diff = neighbor_cost - current_cost
            
            if cost_diff < 0:  # Better solution
                current_deployment = neighbor_deployment
                current_cost = neighbor_cost
                
                if neighbor_cost < best_cost:
                    best_deployment = neighbor_deployment.copy()
                    best_cost = neighbor_cost
            else:
                # Accept worse solution with probability e^(-cost_diff/temp)
                acceptance_probability = math.exp(-cost_diff / temp)
                if random.random() < acceptance_probability:
                    current_deployment = neighbor_deployment
                    current_cost = neighbor_cost
        
        # Cool down
        temp *= cooling_rate
    
    return best_deployment