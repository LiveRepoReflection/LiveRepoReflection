import unittest
from flow_network import solve_flow_network


class FlowNetworkTest(unittest.TestCase):
    def test_simple_case(self):
        graph = {
            1: [(2, 10, 5), (3, 15, 3)],
            2: [(4, 8, 4)],
            3: [(4, 5, 2)],
            4: []
        }

        commodities = [
            {'origin': 1, 'destination': 4, 'demand': 4, 'start_time': 0, 'end_time': 30}
        ]

        time_limit = 30

        result = solve_flow_network(graph, commodities, time_limit)
        self.validate_solution(result, graph, commodities, time_limit)

    def test_no_solution_due_to_capacity(self):
        graph = {
            1: [(2, 5, 1)],
            2: []
        }

        commodities = [
            {'origin': 1, 'destination': 2, 'demand': 3, 'start_time': 0, 'end_time': 10}
        ]

        time_limit = 10

        result = solve_flow_network(graph, commodities, time_limit)
        self.assertEqual(result, {}, "Should return empty dictionary when no solution exists")

    def test_no_solution_due_to_time_window(self):
        graph = {
            1: [(2, 15, 10)],
            2: []
        }

        commodities = [
            {'origin': 1, 'destination': 2, 'demand': 5, 'start_time': 0, 'end_time': 10}
        ]

        time_limit = 20

        result = solve_flow_network(graph, commodities, time_limit)
        self.assertEqual(result, {}, "Should return empty dictionary when no solution exists")

    def test_multiple_commodities(self):
        graph = {
            1: [(2, 5, 5), (3, 3, 3)],
            2: [(4, 4, 4)],
            3: [(4, 7, 3)],
            4: []
        }

        commodities = [
            {'origin': 1, 'destination': 4, 'demand': 3, 'start_time': 0, 'end_time': 20},
            {'origin': 1, 'destination': 4, 'demand': 2, 'start_time': 5, 'end_time': 25}
        ]

        time_limit = 25

        result = solve_flow_network(graph, commodities, time_limit)
        self.validate_solution(result, graph, commodities, time_limit)

    def test_congestion_handling(self):
        graph = {
            1: [(2, 5, 2)],
            2: [(3, 5, 2)],
            3: []
        }

        commodities = [
            {'origin': 1, 'destination': 3, 'demand': 4, 'start_time': 0, 'end_time': 30}
        ]

        time_limit = 30

        result = solve_flow_network(graph, commodities, time_limit)
        self.validate_solution(result, graph, commodities, time_limit)

    def test_delayed_departure(self):
        graph = {
            1: [(2, 5, 2)],
            2: []
        }

        commodities = [
            {'origin': 1, 'destination': 2, 'demand': 4, 'start_time': 10, 'end_time': 30}
        ]

        time_limit = 30

        result = solve_flow_network(graph, commodities, time_limit)
        self.validate_solution(result, graph, commodities, time_limit)
        
        # Check that no departure is before the start time
        if result:
            for flow_events in result.values():
                for event in flow_events:
                    self.assertGreaterEqual(event[0], 10, "Departure time should not be before start time")

    def test_complex_network(self):
        graph = {
            1: [(2, 3, 2), (3, 4, 3)],
            2: [(4, 5, 2), (5, 4, 1)],
            3: [(5, 2, 2)],
            4: [(6, 3, 3)],
            5: [(6, 5, 2)],
            6: []
        }

        commodities = [
            {'origin': 1, 'destination': 6, 'demand': 3, 'start_time': 0, 'end_time': 20},
            {'origin': 3, 'destination': 6, 'demand': 2, 'start_time': 5, 'end_time': 15}
        ]

        time_limit = 20

        result = solve_flow_network(graph, commodities, time_limit)
        self.validate_solution(result, graph, commodities, time_limit)

    def validate_solution(self, solution, graph, commodities, time_limit):
        if not solution:
            # If the solution is empty, we can't validate further
            return

        # Check that the solution includes all commodities
        self.assertEqual(set(solution.keys()), set(range(len(commodities))), 
                         "Solution should include all commodities")

        # Validate each commodity's flow events
        for commodity_id, flow_events in solution.items():
            commodity = commodities[commodity_id]
            total_flow = 0
            
            for event in flow_events:
                departure_time, path, amount = event
                
                # Check that departure time is within the time window
                self.assertGreaterEqual(departure_time, commodity['start_time'], 
                                      f"Departure time {departure_time} not within start time {commodity['start_time']}")
                
                # Check that path is valid and within the graph
                self.assertEqual(path[0], commodity['origin'], 
                               f"Path {path} does not start at origin {commodity['origin']}")
                self.assertEqual(path[-1], commodity['destination'], 
                               f"Path {path} does not end at destination {commodity['destination']}")
                
                # Calculate arrival time and check it's within the time window
                arrival_time = departure_time
                for i in range(len(path) - 1):
                    from_node, to_node = path[i], path[i+1]
                    edge_found = False
                    for edge in graph[from_node]:
                        if edge[0] == to_node:
                            arrival_time += edge[1]
                            edge_found = True
                            break
                    self.assertTrue(edge_found, f"Edge from {from_node} to {to_node} not found in graph")
                
                self.assertLessEqual(arrival_time, commodity['end_time'], 
                                   f"Arrival time {arrival_time} exceeds end time {commodity['end_time']}")
                self.assertLessEqual(arrival_time, time_limit, 
                                   f"Arrival time {arrival_time} exceeds time limit {time_limit}")
                
                # Check that amount is positive
                self.assertGreater(amount, 0, "Flow amount should be positive")
                
                total_flow += amount
            
            # Check that the total flow matches the demand
            self.assertEqual(total_flow, commodity['demand'], 
                           f"Total flow {total_flow} does not match demand {commodity['demand']}")
        
        # Check capacity constraints
        # For simplicity, we'll check each edge at each minute
        # In a real implementation, this would need to track the exact timing of flows
        # This is a simplified version that assumes constant flow rates during travel
        for time in range(time_limit):
            edge_flows = {}
            for commodity_id, flow_events in solution.items():
                for departure_time, path, amount in flow_events:
                    for i in range(len(path) - 1):
                        from_node, to_node = path[i], path[i+1]
                        
                        # Find the travel time for this edge
                        travel_time = None
                        for edge in graph[from_node]:
                            if edge[0] == to_node:
                                travel_time = edge[1]
                                break
                        
                        # Check if the flow is on this edge at the current time
                        edge_start_time = departure_time
                        for j in range(i):
                            prev_from, prev_to = path[j], path[j+1]
                            for edge in graph[prev_from]:
                                if edge[0] == prev_to:
                                    edge_start_time += edge[1]
                                    break
                        
                        edge_end_time = edge_start_time + travel_time
                        
                        if edge_start_time <= time < edge_end_time:
                            edge_key = (from_node, to_node)
                            if edge_key not in edge_flows:
                                edge_flows[edge_key] = 0
                            edge_flows[edge_key] += amount
            
            # Check capacity constraints
            for (from_node, to_node), flow in edge_flows.items():
                capacity = None
                for edge in graph[from_node]:
                    if edge[0] == to_node:
                        capacity = edge[2]
                        break
                
                self.assertLessEqual(flow, capacity, 
                                    f"Flow {flow} exceeds capacity {capacity} on edge ({from_node}, {to_node}) at time {time}")


if __name__ == '__main__':
    unittest.main()