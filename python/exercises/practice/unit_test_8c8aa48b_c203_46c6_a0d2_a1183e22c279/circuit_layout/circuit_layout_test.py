import unittest
from circuit_layout import layout_circuit


class CircuitLayoutTest(unittest.TestCase):
    def verify_layout(self, layout, num_gates, connections, max_delay, gate_delays, output_gates, grid_size):
        # Check if layout is empty (no valid solution)
        if not layout:
            return True  # Empty layout is a valid response for impossible constraints

        # Check layout length
        self.assertEqual(len(layout), num_gates, "Layout must include coordinates for all gates")
        
        # Check all gates are within grid
        for x, y in layout:
            self.assertTrue(0 <= x < grid_size and 0 <= y < grid_size, 
                          f"Gate position ({x}, {y}) outside grid of size {grid_size}")
            self.assertTrue(isinstance(x, int) and isinstance(y, int), 
                          f"Gate position ({x}, {y}) must use integer coordinates")
        
        # Calculate wire lengths
        total_wire_length = 0
        for src, dest in connections:
            if src < 0:  # External input
                input_idx = -src - 1  # Convert negative input index
                src_pos = (input_idx, 0)  # Assume inputs are placed at (idx, 0)
            else:
                src_pos = layout[src]
            
            dest_pos = layout[dest]
            # Manhattan distance
            wire_length = abs(src_pos[0] - dest_pos[0]) + abs(src_pos[1] - dest_pos[1])
            total_wire_length += wire_length
        
        # Check for delay constraints
        # Build adjacency list representation
        adj_list = [[] for _ in range(num_gates)]
        for src, dest in connections:
            if src >= 0:  # Internal gate connection
                adj_list[src].append(dest)
        
        # Check delay for each output gate
        for output_gate in output_gates:
            # For simplicity, we'll check all possible paths to each output
            # In a real test, this would be more sophisticated
            paths = self.find_all_paths(adj_list, connections, output_gate)
            for path in paths:
                delay = sum(gate_delays[gate] for gate in path if gate >= 0)
                self.assertLessEqual(delay, max_delay, 
                                  f"Path to output {output_gate} exceeds max delay: {delay} > {max_delay}")
        
        return total_wire_length
    
    def find_all_paths(self, adj_list, connections, output_gate):
        """Simple helper to find paths to an output gate. Not efficient but works for tests."""
        # Find all gates that directly connect to outputs
        paths = [[output_gate]]
        result = []
        
        # Map of source gates to their destinations
        sources = {}
        for src, dest in connections:
            if src not in sources:
                sources[src] = []
            sources[src].append(dest)
        
        # Process paths
        while paths:
            current_path = paths.pop(0)
            current_node = current_path[0]
            
            # If it's an input or has no inbound connections, we've reached the start
            has_inbound = False
            for src, dest in connections:
                if dest == current_node:
                    has_inbound = True
                    new_path = [src] + current_path
                    if src < 0:  # External input
                        result.append(new_path)
                    else:
                        paths.append(new_path)
            
            if not has_inbound:
                result.append(current_path)
                
        return result
        
    def test_small_circuit_valid_layout(self):
        # Simple 3-gate circuit with AND, OR, NOT
        num_gates = 3
        gate_types = ["AND", "OR", "NOT"]
        connections = [(-1, 0), (-2, 0), (0, 1), (1, 2)]
        gate_delays = [2, 3, 1]
        input_count = 2
        output_gates = [2]
        max_delay = 7
        grid_size = 2 * num_gates
        
        layout = layout_circuit(num_gates, gate_types, connections, gate_delays, 
                               input_count, output_gates, max_delay)
        
        total_wire_length = self.verify_layout(layout, num_gates, connections, 
                                              max_delay, gate_delays, output_gates, grid_size)
        
        if layout:  # Only check wire length if a valid layout is provided
            print(f"Test case 1 wire length: {total_wire_length}")
    
    def test_medium_circuit(self):
        # Medium-sized circuit with 5 gates
        num_gates = 5
        gate_types = ["AND", "OR", "XOR", "NOT", "AND"]
        connections = [(-1, 0), (-2, 0), (-1, 1), (-3, 1), (0, 2), (1, 2), (2, 3), (3, 4)]
        gate_delays = [2, 2, 3, 1, 2]
        input_count = 3
        output_gates = [4]
        max_delay = 10
        grid_size = 2 * num_gates
        
        layout = layout_circuit(num_gates, gate_types, connections, gate_delays, 
                               input_count, output_gates, max_delay)
        
        total_wire_length = self.verify_layout(layout, num_gates, connections, 
                                              max_delay, gate_delays, output_gates, grid_size)
        
        if layout:  # Only check wire length if a valid layout is provided
            print(f"Test case 2 wire length: {total_wire_length}")
    
    def test_impossible_constraints(self):
        # Circuit with impossible delay constraints
        num_gates = 3
        gate_types = ["AND", "OR", "NOT"]
        connections = [(-1, 0), (-2, 0), (0, 1), (1, 2)]
        gate_delays = [2, 3, 1]  # Total delay is 6
        input_count = 2
        output_gates = [2]
        max_delay = 5  # Less than actual delay
        
        layout = layout_circuit(num_gates, gate_types, connections, gate_delays, 
                               input_count, output_gates, max_delay)
        
        self.assertEqual(layout, [], "Expected empty layout for impossible constraints")
    
    def test_multiple_outputs(self):
        # Circuit with multiple output gates
        num_gates = 6
        gate_types = ["AND", "OR", "XOR", "NOT", "AND", "OR"]
        connections = [
            (-1, 0), (-2, 0),  # External inputs to gate 0
            (-1, 1), (-3, 1),  # External inputs to gate 1
            (0, 2), (1, 2),    # Gates 0,1 to gate 2
            (2, 3), (2, 5),    # Gate 2 to gates 3,5
            (3, 4), (1, 4)     # Gates 3,1 to gate 4
        ]
        gate_delays = [1, 2, 3, 1, 2, 1]
        input_count = 3
        output_gates = [4, 5]  # Two outputs
        max_delay = 10
        grid_size = 2 * num_gates
        
        layout = layout_circuit(num_gates, gate_types, connections, gate_delays, 
                               input_count, output_gates, max_delay)
        
        total_wire_length = self.verify_layout(layout, num_gates, connections, 
                                              max_delay, gate_delays, output_gates, grid_size)
        
        if layout:  # Only check wire length if a valid layout is provided
            print(f"Test case 4 wire length: {total_wire_length}")
    
    def test_large_circuit(self):
        # Larger circuit with 10 gates
        num_gates = 10
        gate_types = ["AND", "OR", "XOR", "NOT", "AND", "OR", "XOR", "AND", "NOT", "OR"]
        connections = [
            (-1, 0), (-2, 0),   # External inputs to gate 0
            (-3, 1), (-4, 1),   # External inputs to gate 1
            (0, 2), (1, 2),     # Gates 0,1 to gate 2
            (2, 3),             # Gate 2 to gate 3
            (3, 4), (-5, 4),    # Gate 3, external input to gate 4
            (4, 5), (2, 5),     # Gates 4,2 to gate 5
            (5, 6), (1, 6),     # Gates 5,1 to gate 6
            (6, 7), (4, 7),     # Gates 6,4 to gate 7
            (7, 8),             # Gate 7 to gate 8
            (8, 9), (5, 9)      # Gates 8,5 to gate 9
        ]
        gate_delays = [1, 1, 2, 1, 2, 2, 3, 1, 1, 2]
        input_count = 5
        output_gates = [9]
        max_delay = 15
        grid_size = 2 * num_gates
        
        layout = layout_circuit(num_gates, gate_types, connections, gate_delays, 
                               input_count, output_gates, max_delay)
        
        total_wire_length = self.verify_layout(layout, num_gates, connections, 
                                              max_delay, gate_delays, output_gates, grid_size)
        
        if layout:  # Only check wire length if a valid layout is provided
            print(f"Test case 5 wire length: {total_wire_length}")


if __name__ == '__main__':
    unittest.main()