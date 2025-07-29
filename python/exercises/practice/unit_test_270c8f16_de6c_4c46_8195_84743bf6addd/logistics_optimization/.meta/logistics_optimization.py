import heapq
from collections import defaultdict

def optimize_logistics(warehouses, routes, demands):
    # Build graph representation
    graph = defaultdict(list)
    capacities = {}
    costs = {}
    times = {}
    
    for route in routes:
        src = route['source']
        dest = route['destination']
        graph[src].append(dest)
        capacities[(src, dest)] = route['capacity']
        costs[(src, dest)] = route['cost_per_unit']
        times[(src, dest)] = route['transport_time']
    
    # Check if all demands can be satisfied within deadlines
    for demand in demands:
        if not is_path_possible(graph, times, demand['source'], demand['destination'], demand['deadline']):
            return "Infeasible"
    
    # Convert to minimum cost flow problem
    flow_plan = {}
    total_cost = 0.0
    
    for demand in demands:
        src = demand['source']
        dest = demand['destination']
        quantity = demand['quantity']
        deadline = demand['deadline']
        
        # Find all possible paths within deadline
        paths = find_feasible_paths(graph, times, costs, src, dest, deadline)
        if not paths:
            return "Infeasible"
        
        # Sort paths by cost
        paths.sort(key=lambda x: x[1])
        
        remaining = quantity
        for path, path_cost, path_time in paths:
            if remaining <= 0:
                break
            
            # Find bottleneck capacity
            min_capacity = float('inf')
            for i in range(len(path)-1):
                u = path[i]
                v = path[i+1]
                edge_capacity = capacities[(u, v)]
                min_capacity = min(min_capacity, edge_capacity)
            
            if min_capacity <= 0:
                continue
            
            # Allocate flow
            allocate = min(remaining, min_capacity)
            for i in range(len(path)-1):
                u = path[i]
                v = path[i+1]
                edge = (u, v)
                flow_plan[edge] = flow_plan.get(edge, 0) + allocate
                capacities[edge] -= allocate
            
            total_cost += allocate * path_cost
            remaining -= allocate
        
        if remaining > 0:
            return "Infeasible"
    
    return flow_plan, total_cost

def is_path_possible(graph, times, src, dest, deadline):
    visited = set()
    queue = [(0, src)]
    
    while queue:
        current_time, node = heapq.heappop(queue)
        if node == dest:
            return current_time <= deadline
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor in graph.get(node, []):
            edge_time = times[(node, neighbor)]
            new_time = current_time + edge_time
            heapq.heappush(queue, (new_time, neighbor))
    
    return False

def find_feasible_paths(graph, times, costs, src, dest, deadline):
    paths = []
    visited = set()
    
    def dfs(node, path, current_time, current_cost):
        if node == dest and current_time <= deadline:
            paths.append((path.copy(), current_cost, current_time))
            return
        
        for neighbor in graph.get(node, []):
            if neighbor not in path:
                edge_time = times[(node, neighbor)]
                edge_cost = costs[(node, neighbor)]
                new_time = current_time + edge_time
                new_cost = current_cost + edge_cost
                if new_time <= deadline:
                    path.append(neighbor)
                    dfs(neighbor, path, new_time, new_cost)
                    path.pop()
    
    dfs(src, [src], 0, 0)
    return paths