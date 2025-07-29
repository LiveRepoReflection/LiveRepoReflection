from collections import deque

def find_optimal_path(grid_snapshots, battery_capacity, move_cost):
    best_path = None
    best_moves = float('inf')
    
    # Four possible directions: up, down, left, right.
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # Process each snapshot independently.
    for snapshot in grid_snapshots:
        grid, remaining_moves, snapshot_battery = snapshot
        
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        # Locate start (S) and delivery (D) positions.
        start = None
        dest = None
        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == "S":
                    start = (i, j)
                elif grid[i][j] == "D":
                    dest = (i, j)
        if start is None or dest is None:
            continue
        
        # Breadth-first search (BFS) with state: (row, col, battery, moves, path)
        queue = deque()
        queue.append((start[0], start[1], snapshot_battery, 0, [start]))
        visited = {}
        visited[(start[0], start[1], snapshot_battery)] = 0
        
        found_path = None
        
        while queue:
            r, c, battery, moves, path = queue.popleft()
            if (r, c) == dest:
                if moves <= remaining_moves:
                    found_path = path
                    break
            if moves == remaining_moves:
                continue
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if nr < 0 or nr >= rows or nc < 0 or nc >= cols:
                    continue
                cell = grid[nr][nc]
                if cell == "O":
                    continue
                if battery < move_cost:
                    continue
                new_battery = battery - move_cost
                # Recharge at charging station.
                if cell == "C":
                    new_battery = battery_capacity
                new_moves = moves + 1
                if new_moves > remaining_moves:
                    continue
                state = (nr, nc, new_battery)
                if state in visited and visited[state] <= new_moves:
                    continue
                visited[state] = new_moves
                new_path = path + [(nr, nc)]
                queue.append((nr, nc, new_battery, new_moves, new_path))
        if found_path is not None:
            if len(found_path) - 1 < best_moves:
                best_moves = len(found_path) - 1
                best_path = found_path
    return best_path if best_path is not None else []