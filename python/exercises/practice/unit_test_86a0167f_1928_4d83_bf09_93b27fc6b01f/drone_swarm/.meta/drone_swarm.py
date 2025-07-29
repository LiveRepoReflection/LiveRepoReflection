def next_target(drone_id, current_location, communication_range, known_drones, explored_areas, poi_candidates, global_bounds, battery_level):
    def is_within_bounds(point, bounds):
        (min_x, min_y), (max_x, max_y) = bounds
        x, y = point
        return min_x <= x <= max_x and min_y <= y <= max_y

    def movement_cost(src, dst):
        dx = abs(dst[0] - src[0])
        dy = abs(dst[1] - src[1])
        return (dx + dy) * 0.001

    # 1. Prioritize unexplored POI candidates.
    poi_unexplored = []
    for pt in poi_candidates:
        if pt not in explored_areas and is_within_bounds(pt, global_bounds):
            cost = movement_cost(current_location, pt)
            if battery_level >= cost:
                poi_unexplored.append((pt, cost))
    if poi_unexplored:
        poi_unexplored.sort(key=lambda x: x[1])
        return poi_unexplored[0][0]

    # 2. Consider all POI candidates if any are feasible.
    poi_feasible = []
    for pt in poi_candidates:
        if is_within_bounds(pt, global_bounds):
            cost = movement_cost(current_location, pt)
            if battery_level >= cost:
                poi_feasible.append((pt, cost))
    if poi_feasible:
        poi_feasible.sort(key=lambda x: x[1])
        return poi_feasible[0][0]

    # 3. Explore adjacent cells that have not been explored.
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            candidate = (current_location[0] + dx, current_location[1] + dy)
            if is_within_bounds(candidate, global_bounds):
                cost = movement_cost(current_location, candidate)
                if battery_level >= cost and candidate not in explored_areas:
                    neighbors.append((candidate, cost))
    if neighbors:
        neighbors.sort(key=lambda x: x[1])
        return neighbors[0][0]

    # 4. If no unexplored neighbors, consider any adjacent cell.
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            candidate = (current_location[0] + dx, current_location[1] + dy)
            if is_within_bounds(candidate, global_bounds):
                cost = movement_cost(current_location, candidate)
                if battery_level >= cost:
                    neighbors.append((candidate, cost))
    if neighbors:
        neighbors.sort(key=lambda x: x[1])
        return neighbors[0][0]

    # 5. If no valid move is available, remain in current location.
    return current_location