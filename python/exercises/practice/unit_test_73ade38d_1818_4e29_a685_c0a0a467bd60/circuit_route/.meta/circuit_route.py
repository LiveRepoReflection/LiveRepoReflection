import heapq
from collections import deque

def optimal_circuit_routing(rows, cols, components, blocked):
    if not rows or not cols:
        return -1
    
    # Create grid with blocked cells marked
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for (r, c) in blocked:
        grid[r][c] = -1
    
    # Check if any component start/end is blocked
    for start, end in components:
        if grid[start[0]][start[1]] == -1 or grid[end[0]][end[1]] == -1:
            return -1
    
    # Binary search for minimum maximum wire length
    low = 0
    high = rows + cols - 2  # Maximum possible Manhattan distance
    result = -1
    
    while low <= high:
        mid = (low + high) // 2
        if is_routing_possible(rows, cols, components, grid, mid):
            result = mid
            high = mid - 1
        else:
            low = mid + 1
    
    return result

def is_routing_possible(rows, cols, components, grid, max_length):
    # Make a deep copy of the grid to track used cells
    used = [row[:] for row in grid]
    component_order = sorted(range(len(components)), 
                           key=lambda i: manhattan_distance(*components[i]))
    
    for i in component_order:
        start, end = components[i]
        if not find_path(start, end, used, max_length):
            return False
    return True

def find_path(start, end, used, max_length):
    if start == end:
        return True
    
    rows = len(used)
    cols = len(used[0])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
    heap = []
    heapq.heappush(heap, (manhattan_distance(start, end), 0, start))
    visited = set()
    visited.add(start)
    
    while heap:
        _, length, (r, c) = heapq.heappop(heap)
        
        if (r, c) == end:
            return True
        
        if length >= max_length:
            continue
            
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if (nr, nc) not in visited and used[nr][nc] != -1:
                    # Only mark as used if not start/end of other components
                    if (nr, nc) == end or used[nr][nc] == 0:
                        visited.add((nr, nc))
                        heapq.heappush(heap, 
                                      (manhattan_distance((nr, nc), end), 
                                       length + 1, 
                                       (nr, nc)))
    
    return False

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])