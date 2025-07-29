from collections import defaultdict, deque
import heapq


def layout_circuit(num_gates, gate_types, connections, gate_delays, input_count, output_gates, max_delay):
    """
    Design an optimal IC circuit layout to minimize total wire length.
    
    Args:
        num_gates: Number of logic gates in the circuit.
        gate_types: List of gate types (AND, OR, XOR, NOT).
        connections: List of connections between gates as (source, destination) tuples.
        gate_delays: List of propagation delays for each gate.
        input_count: Number of external inputs to the circuit.
        output_gates: List of gate indices that are circuit outputs.
        max_delay: Maximum allowed propagation delay from input to output.
        
    Returns:
        List of (x, y) coordinates for each gate, or empty list if not possible.
    """
    # Check if the circuit is acyclic and compute topological sorting
    adjacency_list = defaultdict(list)
    in_degree = [0] * num_gates
    
    # Build adjacency list from connections
    for src, dest in connections:
        if src >= 0:  # Only internal gates, not inputs
            adjacency_list[src].append(dest)
            in_degree[dest] += 1
    
    # Perform topological sort
    topo_order = []
    queue = deque([i for i in range(num_gates) if in_degree[i] == 0])
    
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        
        for neighbor in adjacency_list[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # Check if the graph has a cycle
    if len(topo_order) != num_gates:
        return []  # Circuit has a cycle
    
    # Verify gate input constraints
    gate_inputs = defaultdict(int)
    for src, dest in connections:
        if src >= 0 or src < 0:  # Count all inputs including external ones
            gate_inputs[dest] += 1
    
    for i, gate_type in enumerate(gate_types):
        if gate_type == "NOT" and gate_inputs[i] != 1:
            return []  # NOT gates must have exactly 1 input
        elif gate_type != "NOT" and gate_inputs[i] > 2:
            return []  # Other gates can have at most 2 inputs
    
    # Check delay constraints
    max_delays = compute_max_delays(num_gates, connections, gate_delays, topo_order)
    
    for output_gate in output_gates:
        if max_delays[output_gate] > max_delay:
            return []  # Delay constraint violated
    
    # Position external inputs at fixed locations
    input_positions = [(i, 0) for i in range(input_count)]
    
    # Assign coordinates to gates using layered approach based on topological order
    grid_size = 2 * num_gates  # As per constraint
    
    # Use force-directed placement to assign initial positions
    positions = force_directed_placement(
        num_gates, connections, input_count, topo_order, grid_size
    )
    
    # Refine positions with simulated annealing to minimize wire length
    final_positions = simulated_annealing(
        positions, connections, input_count, grid_size
    )
    
    return final_positions


def compute_max_delays(num_gates, connections, gate_delays, topo_order):
    """
    Compute the maximum delay from any input to each gate.
    """
    # Initialize delays
    max_delays = [0] * num_gates
    
    # Process gates in topological order
    for gate in topo_order:
        # Find all gates that feed into this gate
        for src, dest in connections:
            if dest == gate and src >= 0:  # Internal gate connection
                max_delays[gate] = max(max_delays[gate], max_delays[src] + gate_delays[gate])
        
        # If this is the first gate in a path, just use its own delay
        if max_delays[gate] == 0 and gate_delays[gate] > 0:
            max_delays[gate] = gate_delays[gate]
    
    return max_delays


def force_directed_placement(num_gates, connections, input_count, topo_order, grid_size):
    """
    Use force-directed algorithm to find initial positions for gates.
    """
    # Initialize random positions for gates
    import random
    random.seed(42)  # For reproducible results
    
    positions = []
    for _ in range(num_gates):
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        positions.append((x, y))
    
    # Define fixed positions for inputs
    input_positions = [(i, 0) for i in range(input_count)]
    
    # Parameters for force-directed placement
    iterations = 100
    k = grid_size / (num_gates**0.5)  # Optimal distance between nodes
    
    for _ in range(iterations):
        # Calculate repulsive forces between all gate pairs
        forces = [(0, 0) for _ in range(num_gates)]
        
        for i in range(num_gates):
            for j in range(num_gates):
                if i != j:
                    dx = positions[i][0] - positions[j][0]
                    dy = positions[i][1] - positions[j][1]
                    distance = max(0.1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
                    
                    # Repulsive force: inversely proportional to distance
                    force = k**2 / distance
                    
                    # Apply force vector
                    if distance > 0:
                        fx = force * dx / distance
                        fy = force * dy / distance
                        forces[i] = (forces[i][0] + fx, forces[i][1] + fy)
        
        # Calculate attractive forces for connected gates
        for src, dest in connections:
            if src >= 0:  # Internal gate connection
                dx = positions[src][0] - positions[dest][0]
                dy = positions[src][1] - positions[dest][1]
                distance = max(0.1, (dx**2 + dy**2)**0.5)
                
                # Attractive force: proportional to distance
                force = distance**2 / k
                
                # Apply force vector
                if distance > 0:
                    fx = force * dx / distance
                    fy = force * dy / distance
                    
                    forces[src] = (forces[src][0] - fx, forces[src][1] - fy)
                    forces[dest] = (forces[dest][0] + fx, forces[dest][1] + fy)
            else:  # External input connection
                input_idx = -src - 1
                input_pos = input_positions[input_idx]
                
                dx = input_pos[0] - positions[dest][0]
                dy = input_pos[1] - positions[dest][1]
                distance = max(0.1, (dx**2 + dy**2)**0.5)
                
                # Attractive force for inputs
                force = distance**2 / k
                
                if distance > 0:
                    fx = force * dx / distance
                    fy = force * dy / distance
                    forces[dest] = (forces[dest][0] + fx, forces[dest][1] + fy)
        
        # Update positions based on forces
        for i in range(num_gates):
            fx, fy = forces[i]
            
            # Limit maximum movement per iteration
            max_movement = 1.0
            fx = max(-max_movement, min(fx, max_movement))
            fy = max(-max_movement, min(fy, max_movement))
            
            new_x = int(max(0, min(grid_size - 1, positions[i][0] + fx)))
            new_y = int(max(0, min(grid_size - 1, positions[i][1] + fy)))
            
            positions[i] = (new_x, new_y)
    
    # Ensure no overlapping positions by using a greedy approach
    used_positions = set()
    final_positions = []
    
    for gate in topo_order:
        x, y = positions[gate]
        
        # Find closest available position if current one is taken
        if (x, y) in used_positions:
            closest_pos = find_closest_available_position(x, y, used_positions, grid_size)
            x, y = closest_pos
        
        used_positions.add((x, y))
        final_positions.append((x, y))
    
    return final_positions


def find_closest_available_position(x, y, used_positions, grid_size):
    """
    Find the closest available position to (x, y) that is not in used_positions.
    """
    # Use a priority queue for finding closest position
    pq = [(0, x, y)]  # (distance, x, y)
    visited = set()
    
    while pq:
        dist, curr_x, curr_y = heapq.heappop(pq)
        
        if (curr_x, curr_y) not in used_positions and 0 <= curr_x < grid_size and 0 <= curr_y < grid_size:
            return (curr_x, curr_y)
        
        if (curr_x, curr_y) in visited:
            continue
        
        visited.add((curr_x, curr_y))
        
        # Try adjacent positions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = curr_x + dx, curr_y + dy
            if 0 <= new_x < grid_size and 0 <= new_y < grid_size and (new_x, new_y) not in visited:
                new_dist = dist + 1
                heapq.heappush(pq, (new_dist, new_x, new_y))
    
    # If no position is found (unlikely), return a default position
    for i in range(grid_size):
        for j in range(grid_size):
            if (i, j) not in used_positions:
                return (i, j)
    
    return (0, 0)  # Fallback


def simulated_annealing(initial_positions, connections, input_count, grid_size):
    """
    Use simulated annealing to optimize gate positions for minimal wire length.
    """
    import random
    import math
    
    random.seed(42)
    
    # Define fixed positions for inputs
    input_positions = [(i, 0) for i in range(input_count)]
    
    current_positions = initial_positions.copy()
    current_wire_length = calculate_total_wire_length(current_positions, connections, input_count)
    
    best_positions = current_positions.copy()
    best_wire_length = current_wire_length
    
    # Simulated annealing parameters
    temperature = 100.0
    cooling_rate = 0.95
    iterations_per_temp = 100
    min_temperature = 0.1
    
    while temperature > min_temperature:
        for _ in range(iterations_per_temp):
            # Select a random gate to move
            gate_idx = random.randint(0, len(current_positions) - 1)
            
            # Save current position
            old_x, old_y = current_positions[gate_idx]
            
            # Generate new position by moving slightly
            new_x = random.randint(max(0, old_x - 2), min(grid_size - 1, old_x + 2))
            new_y = random.randint(max(0, old_y - 2), min(grid_size - 1, old_y + 2))
            
            # Skip if position is already used
            if (new_x, new_y) in set(current_positions) - {(old_x, old_y)}:
                continue
            
            # Try the new position
            current_positions[gate_idx] = (new_x, new_y)
            new_wire_length = calculate_total_wire_length(current_positions, connections, input_count)
            
            # Decide whether to accept the move
            delta = new_wire_length - current_wire_length
            
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                # Accept the move
                current_wire_length = new_wire_length
                
                # Update best solution if improved
                if new_wire_length < best_wire_length:
                    best_wire_length = new_wire_length
                    best_positions = current_positions.copy()
            else:
                # Revert the move
                current_positions[gate_idx] = (old_x, old_y)
        
        # Cool down
        temperature *= cooling_rate
    
    return best_positions


def calculate_total_wire_length(positions, connections, input_count):
    """
    Calculate the total Manhattan distance of all connections.
    """
    total_length = 0
    
    # Define fixed positions for inputs
    input_positions = [(i, 0) for i in range(input_count)]
    
    for src, dest in connections:
        if src < 0:  # External input
            input_idx = -src - 1
            src_pos = input_positions[input_idx]
        else:
            src_pos = positions[src]
        
        dest_pos = positions[dest]
        
        # Manhattan distance
        wire_length = abs(src_pos[0] - dest_pos[0]) + abs(src_pos[1] - dest_pos[1])
        total_length += wire_length
    
    return total_length