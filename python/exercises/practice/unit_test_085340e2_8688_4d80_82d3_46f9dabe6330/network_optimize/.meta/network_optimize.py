from collections import defaultdict
import heapq
from typing import Dict, List, Set, Tuple

def optimize_network_flow(graph: Dict, requests: List[Dict], server_properties: Dict) -> List[List[str]]:
    def get_min_latency_path(source: str, dest: str, size: int, content_id: str, 
                            visited_loads: Dict[str, int]) -> Tuple[List[str], float]:
        """Find the path with minimum latency using Dijkstra's algorithm while respecting constraints."""
        if source == dest:
            return [source], 0

        distances = {node: float('infinity') for node in graph}
        distances[source] = 0
        pq = [(0, source, [source])]
        seen = set()

        while pq:
            current_distance, current_node, path = heapq.heappop(pq)
            
            if current_node in seen:
                continue
                
            seen.add(current_node)
            
            if current_node == dest:
                # Verify the path satisfies all constraints
                valid = True
                for node in path:
                    # Check content availability
                    if node == dest and not server_properties[node]['content_availability'].get(content_id, False):
                        valid = False
                        break
                    # Check server load constraints
                    if visited_loads[node] + size > server_properties[node]['max_load']:
                        valid = False
                        break
                    # Check edge capacity constraints
                    if len(path) > 1:
                        for i in range(len(path)-1):
                            if graph[path[i]][path[i+1]]['capacity'] < size:
                                valid = False
                                break
                if valid:
                    return path, current_distance
                continue

            for neighbor, edge_data in graph[current_node].items():
                if neighbor in seen:
                    continue
                    
                # Check if edge has enough capacity
                if edge_data['capacity'] < size:
                    continue

                # Calculate new distance including latency
                distance = current_distance + edge_data['latency']
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor, path + [neighbor]))

        return [], float('infinity')

    def can_fulfill_request(request: Dict, visited_loads: Dict[str, int]) -> bool:
        """Check if a request can be fulfilled given current network state."""
        source = request['source_location']
        dest = request['destination_location']
        size = request['size']
        content_id = request['content_id']

        # Check if destination has the content
        if not server_properties[dest]['content_availability'].get(content_id, False):
            return False

        # Check if source and intermediate nodes have enough capacity
        for node in graph:
            if visited_loads[node] + size > server_properties[node]['max_load']:
                return False

        return True

    # Initialize result and tracking structures
    result = []
    visited_loads = defaultdict(int)

    # Process each request
    for request in requests:
        source = request['source_location']
        dest = request['destination_location']
        size = request['size']
        
        # Check if request can be fulfilled
        if not can_fulfill_request(request, visited_loads):
            result.append([])
            continue

        # Find optimal path
        path, total_latency = get_min_latency_path(
            source, dest, size, request['content_id'], visited_loads
        )

        if not path:
            result.append([])
            continue

        # Update loads for the path
        for node in path:
            visited_loads[node] += size

        result.append(path)

    return result

def verify_solution(graph: Dict, requests: List[Dict], server_properties: Dict, 
                   paths: List[List[str]]) -> bool:
    """Verify if the solution satisfies all constraints."""
    if len(paths) != len(requests):
        return False

    visited_loads = defaultdict(int)

    for request, path in zip(requests, paths):
        if not path:  # Skip empty paths
            continue

        size = request['size']
        content_id = request['content_id']

        # Verify path starts and ends at correct locations
        if path[0] != request['source_location'] or path[-1] != request['destination_location']:
            return False

        # Verify content availability at destination
        if not server_properties[path[-1]]['content_availability'].get(content_id, False):
            return False

        # Verify server loads
        for node in path:
            visited_loads[node] += size
            if visited_loads[node] > server_properties[node]['max_load']:
                return False

        # Verify edge capacity constraints
        for i in range(len(path) - 1):
            if graph[path[i]][path[i+1]]['capacity'] < size:
                return False

    return True