import heapq
from collections import deque

def find_paths(grid_size, terminal_pairs, obstacles, wire_width):
    """
    Find shortest paths for multiple terminal pairs on a grid with obstacles and wire spacing constraints.
    Uses A* algorithm with priority queuing and dynamic obstacle tracking.
    """
    results = []
    occupied = set(obstacles)
    half_width = wire_width // 2
    
    for pair in terminal_pairs:
        start, end = pair
        path = find_single_path(grid_size, start, end, occupied, obstacles, wire_width)
        results.append(path)
        if path:
            # Add the new path's occupied positions to the set
            for point in path:
                for dx in range(-half_width, half_width + 1):
                    for dy in range(-half_width, half_width + 1):
                        x, y = point[0] + dx, point[1] + dy
                        if 0 <= x < grid_size and 0 <= y < grid_size:
                            occupied.add((x, y))
    return results

def find_single_path(grid_size, start, end, occupied, obstacles, wire_width):
    """Find shortest path for a single terminal pair using A* algorithm."""
    if start == end:
        return [start]
    
    half_width = wire_width // 2
    closed_set = set()
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == end:
            return reconstruct_path(came_from, current)
        
        closed_set.add(current)
        
        for neighbor in get_neighbors(current, grid_size, wire_width, occupied, obstacles):
            if neighbor in closed_set:
                continue
                
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in [i[1] for i in open_set] or tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []  # No path found

def get_neighbors(point, grid_size, wire_width, occupied, obstacles):
    """Get valid neighboring points considering wire width and obstacles."""
    x, y = point
    half_width = wire_width // 2
    neighbors = []
    
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # 4-directional movement
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            valid = True
            # Check if any point in the wire width square is occupied
            for wx in range(nx - half_width, nx + half_width + 1):
                for wy in range(ny - half_width, ny + half_width + 1):
                    if (wx < 0 or wx >= grid_size or wy < 0 or wy >= grid_size or
                        (wx, wy) in occupied or (wx, wy) in obstacles):
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                neighbors.append((nx, ny))
    return neighbors

def heuristic(point, end):
    """Manhattan distance heuristic for A* algorithm."""
    return abs(point[0] - end[0]) + abs(point[1] - end[1])

def reconstruct_path(came_from, current):
    """Reconstruct path from start to end using came_from dictionary."""
    path = deque()
    while current in came_from:
        path.appendleft(current)
        current = came_from[current]
    path.appendleft(current)
    return list(path)