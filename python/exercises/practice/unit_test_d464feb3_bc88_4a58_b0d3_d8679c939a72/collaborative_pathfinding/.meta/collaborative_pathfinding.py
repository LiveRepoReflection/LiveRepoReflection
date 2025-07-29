import heapq
import time
import math

def simulate(width, height, n, agent_configurations, static_obstacles, communication_range, time_budget, max_steps):
    # Convert time_budget from milliseconds to seconds
    time_limit = time_budget / 1000.0

    # Initialize agents: each agent is a dict with current position, target, and path history.
    agents = []
    for config in agent_configurations:
        start_x, start_y, target_x, target_y = config
        agents.append({
            "current": (start_x, start_y),
            "target": (target_x, target_y),
            "path": [(start_x, start_y)]
        })

    # Convert static_obstacles to a set of positions if not already in that format.
    obstacles = set(static_obstacles)

    # Simulation loop: each step, each agent makes a move.
    for step in range(1, max_steps):
        # Record proposals for moves: agent index -> candidate next position.
        proposals = [None] * n

        # Create a set of positions occupied at the start of the step.
        current_positions = {i: agent["current"] for i, agent in enumerate(agents)}

        # Each agent plans its move if it has not yet reached its destination.
        for i, agent in enumerate(agents):
            if agent["current"] == agent["target"]:
                proposals[i] = agent["current"]
                continue

            decision_start = time.perf_counter()
            # Dynamic obstacles: positions of other agents (excluding self)
            dynamic_obstacles = {pos for j, pos in current_positions.items() if j != i}
            # Combine static and dynamic obstacles
            all_obstacles = obstacles.union(dynamic_obstacles)
            # Run A* search from current to target
            path = a_star(agent["current"], agent["target"], all_obstacles, width, height)
            decision_end = time.perf_counter()
            elapsed = decision_end - decision_start
            # If decision making takes longer than allowed time_budget, stay in place.
            if elapsed > time_limit or not path or len(path) < 2:
                proposals[i] = agent["current"]
            else:
                # Next move is the second element in the path
                proposals[i] = path[1]

        # Resolve conflicts: if more than one agent propose the same move, allow only the one with the lowest index.
        move_counts = {}
        for pos in proposals:
            move_counts[pos] = move_counts.get(pos, 0) + 1

        final_moves = [None] * n
        for i, proposed in enumerate(proposals):
            # If multiple agents try to move to the same cell, the one with the lowest index gets to move,
            # others remain in place.
            if move_counts[proposed] == 1:
                final_moves[i] = proposed
            else:
                # Check if this agent is the first among agents that proposed this move.
                first_agent = min([j for j, pos in enumerate(proposals) if pos == proposed])
                if i == first_agent:
                    final_moves[i] = proposed
                else:
                    final_moves[i] = agents[i]["current"]

        # Update agents positions and record the move.
        for i, agent in enumerate(agents):
            agent["current"] = final_moves[i]
            agent["path"].append(final_moves[i])

        # Check if all agents have reached their target.
        if all(agent["current"] == agent["target"] for agent in agents):
            break

    # Return list of paths for all agents.
    return [agent["path"] for agent in agents]

def a_star(start, goal, obstacles, width, height):
    # Check if start or goal is blocked
    if start in obstacles or goal in obstacles:
        return None

    # Moves: 8-directional moves (dx, dy)
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),          (0, 1),
             (1, -1),  (1, 0), (1, 1)]
    
    def in_bounds(pos):
        x, y = pos
        return 0 <= x < width and 0 <= y < height

    def heuristic(a, b):
        # Use Euclidean distance as heuristic.
        return math.hypot(a[0] - b[0], a[1] - b[1])
    
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    
    while open_set:
        _, current_cost, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for dx, dy in moves:
            neighbor = (current[0] + dx, current[1] + dy)
            if not in_bounds(neighbor):
                continue
            if neighbor in obstacles:
                continue
            tentative_g_score = g_score[current] + math.hypot(dx, dy)
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor))
    return None

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    total_path.reverse()
    return total_path