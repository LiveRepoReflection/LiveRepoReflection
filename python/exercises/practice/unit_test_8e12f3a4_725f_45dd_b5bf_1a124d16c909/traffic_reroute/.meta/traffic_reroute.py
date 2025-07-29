from collections import defaultdict, deque
import heapq
from typing import Dict, List, Set, Tuple
import math

class Graph:
    def __init__(self):
        self.edges = defaultdict(list)
        self.capacities = {}
        self.flows = {}
        
    def add_edge(self, u: int, v: int, capacity: int, flow: int):
        self.edges[u].append(v)
        self.edges[v].append(u)  # Add reverse edge for residual graph
        self.capacities[(u, v)] = capacity
        self.capacities[(v, u)] = 0  # Reverse edge capacity
        self.flows[(u, v)] = flow
        self.flows[(v, u)] = -flow  # Reverse flow

def calculate_travel_time(capacity: int, flow: int) -> float:
    return 1.0 / (capacity - flow + 1)

def find_shortest_path(graph: Graph, source: int, sink: int, flows: Dict) -> Tuple[List[int], float]:
    distances = {node: float('infinity') for node in graph.edges}
    distances[source] = 0
    pq = [(0, source)]
    predecessors = {source: None}
    
    while pq:
        current_distance, current = heapq.heappop(pq)
        
        if current == sink:
            path = []
            while current is not None:
                path.append(current)
                current = predecessors[current]
            return path[::-1], current_distance
            
        if current_distance > distances[current]:
            continue
            
        for neighbor in graph.edges[current]:
            residual_capacity = graph.capacities[(current, neighbor)] - flows.get((current, neighbor), 0)
            if residual_capacity <= 0:
                continue
                
            travel_time = calculate_travel_time(graph.capacities[(current, neighbor)],
                                             flows.get((current, neighbor), 0))
            distance = current_distance + travel_time
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))
                
    return [], float('infinity')

def get_path_capacity(graph: Graph, path: List[int], flows: Dict) -> int:
    min_capacity = float('infinity')
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        residual_capacity = graph.capacities[(u, v)] - flows.get((u, v), 0)
        min_capacity = min(min_capacity, residual_capacity)
    return min_capacity

def optimize_traffic_flow(input_data: Dict) -> Dict:
    # Input validation
    if not all(isinstance(node, int) for node in input_data["nodes"]):
        raise ValueError("All nodes must be integers")
    
    if any(edge["capacity"] < 0 or edge["flow"] < 0 for edge in input_data["edges"]):
        raise ValueError("Capacities and flows must be non-negative")

    # Initialize graph
    graph = Graph()
    current_flows = {}
    
    # Build initial graph
    for edge in input_data["edges"]:
        src, dst = edge["source"], edge["destination"]
        graph.add_edge(src, dst, edge["capacity"], edge["flow"])
        current_flows[(src, dst)] = edge["flow"]
        
    # Process demands
    demands = input_data["demands"]
    total_demand = sum(demand["demand"] for demand in demands)
    
    if total_demand == 0:
        return {"edges": [{"source": e["source"], 
                          "destination": e["destination"],
                          "flow": e["flow"]} for e in input_data["edges"]]}
    
    # Process each demand proportionally
    for demand in demands:
        origin, destination = demand["origin"], demand["destination"]
        target_flow = demand["demand"]
        
        while target_flow > 0:
            path, cost = find_shortest_path(graph, origin, destination, current_flows)
            
            if not path:
                break
                
            flow = min(target_flow, get_path_capacity(graph, path, current_flows))
            
            # Update flows along the path
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                current_flows[(u, v)] = current_flows.get((u, v), 0) + flow
                current_flows[(v, u)] = current_flows.get((v, u), 0) - flow
                
            target_flow -= flow
    
    # Prepare output
    result_edges = []
    for edge in input_data["edges"]:
        src, dst = edge["source"], edge["destination"]
        result_edges.append({
            "source": src,
            "destination": dst,
            "flow": current_flows.get((src, dst), 0)
        })
    
    return {"edges": result_edges}