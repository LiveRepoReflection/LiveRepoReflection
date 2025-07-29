from collections import defaultdict, deque
from heapq import heappush, heappop
import math

def find_quantum_paths(grid, qubits):
    if len(qubits) <= 1:
        return []
    
    # Initialize necessary data structures
    height, width = len(grid), len(grid[0])
    paths = []
    mst_edges = _get_minimum_spanning_tree(qubits)
    
    # Sort edges by manhattan distance to prioritize shorter connections
    mst_edges.sort(key=lambda x: _manhattan_distance(x[0], x[1]))
    
    # Route each edge in the MST
    for start, end in mst_edges:
        path = _find_path(grid, start, end, paths)
        if path:
            paths.append(path)
        else:
            return []  # If any connection fails, return empty list
            
    return _optimize_paths(paths, grid)

def _get_minimum_spanning_tree(qubits):
    """Implements Kruskal's algorithm to find MST"""
    edges = []
    for i in range(len(qubits)):
        for j in range(i + 1, len(qubits)):
            dist = _manhattan_distance(qubits[i], qubits[j])
            edges.append((qubits[i], qubits[j], dist))
    
    edges.sort(key=lambda x: x[2])
    
    # Initialize disjoint set
    parent = {qubit: qubit for qubit in qubits}
    rank = {qubit: 0 for qubit in qubits}
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return False
        if rank[px] < rank[py]:
            px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]:
            rank[px] += 1
        return True
    
    mst = []
    for u, v, _ in edges:
        if union(u, v):
            mst.append((u, v))
            if len(mst) == len(qubits) - 1:
                break
                
    return mst

def _find_path(grid, start, end, existing_paths):
    """A* pathfinding algorithm with collision avoidance"""
    height, width = len(grid), len(grid[0])
    
    def heuristic(pos):
        return _manhattan_distance(pos, end)
    
    # Create collision map
    collision_cost = defaultdict(int)
    for path in existing_paths:
        for pos in path:
            collision_cost[pos] += 100
    
    queue = [(0 + heuristic(start), 0, start, [start])]
    visited = set()
    
    while queue:
        _, cost, current, path = heappop(queue)
        
        if current == end:
            return path
            
        if current in visited:
            continue
            
        visited.add(current)
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = current[0] + dx, current[1] + dy
            if (0 <= new_x < height and 0 <= new_y < width and 
                grid[new_x][new_y] == 0 and 
                (new_x, new_y) not in visited):
                
                new_cost = cost + 1 + collision_cost[(new_x, new_y)]
                new_path = path + [(new_x, new_y)]
                heappush(queue, (new_cost + heuristic((new_x, new_y)),
                                new_cost,
                                (new_x, new_y),
                                new_path))
    
    return None

def _optimize_paths(paths, grid):
    """Post-process paths to reduce intersections and total length"""
    def can_remove_point(path, i):
        if i == 0 or i == len(path) - 1:
            return False
        prev, curr, next_ = path[i-1], path[i], path[i+1]
        # Check if removing the point maintains valid path
        return (_manhattan_distance(prev, next_) == 
                _manhattan_distance(prev, curr) + _manhattan_distance(curr, next_))
    
    optimized = []
    for path in paths:
        # Remove unnecessary points
        i = 1
        while i < len(path) - 1:
            if can_remove_point(path, i):
                path.pop(i)
            else:
                i += 1
        optimized.append(path)
    
    return optimized

def _manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])