import unittest
from traffic_genius import optimize_traffic_flow

class TestTrafficGenius(unittest.TestCase):
    
    def test_basic_flow(self):
        """Test a simple graph with constant capacities."""
        def capacity_AB(time):
            return 10
        
        def capacity_BC(time):
            return 8
        
        graph = {"A": {"B": capacity_AB}, "B": {"C": capacity_BC}, "C": {}}
        sources = ["A"]
        destinations = ["C"]
        road_closures = []
        emergency_requests = []
        time = 3
        
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")], 8)
        self.assertEqual(flow[("B", "C")], 8)
    
    def test_dynamic_capacity(self):
        """Test a graph with dynamic capacities."""
        def capacity_AB(time):
            if time < 5:
                return 10
            else:
                return 5
        
        def capacity_BC(time):
            return 8
        
        graph = {"A": {"B": capacity_AB}, "B": {"C": capacity_BC}, "C": {}}
        sources = ["A"]
        destinations = ["C"]
        road_closures = []
        emergency_requests = []
        
        # Before capacity change
        time = 3
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")], 8)
        self.assertEqual(flow[("B", "C")], 8)
        
        # After capacity change
        time = 6
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")], 5)
        self.assertEqual(flow[("B", "C")], 5)
    
    def test_road_closure(self):
        """Test a graph with road closures."""
        def capacity_AB(time):
            return 10
        
        def capacity_BC(time):
            return 8
        
        def capacity_AC(time):
            return 5
        
        graph = {
            "A": {"B": capacity_AB, "C": capacity_AC}, 
            "B": {"C": capacity_BC}, 
            "C": {}
        }
        sources = ["A"]
        destinations = ["C"]
        road_closures = [(10, 20, "A", "B")]
        emergency_requests = []
        
        # Before road closure
        time = 5
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")] + flow[("A", "C")], 13)
        self.assertEqual(flow[("B", "C")] + flow[("A", "C")], 13)
        
        # During road closure
        time = 15
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow.get(("A", "B"), 0), 0)
        self.assertEqual(flow[("A", "C")], 5)
    
    def test_emergency_vehicle(self):
        """Test a graph with emergency vehicles."""
        def capacity_AB(time):
            return 10
        
        def capacity_BC(time):
            return 8
        
        graph = {"A": {"B": capacity_AB}, "B": {"C": capacity_BC}, "C": {}}
        sources = ["A"]
        destinations = ["C"]
        road_closures = []
        emergency_requests = [(15, "A", "C", 2, ["A", "B", "C"])]
        
        # Before emergency request
        time = 10
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")], 8)
        self.assertEqual(flow[("B", "C")], 8)
        
        # During emergency request
        time = 15
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")], 8)
        self.assertEqual(flow[("B", "C")], 8)
        # Ensure emergency vehicles are prioritized
        self.assertTrue(flow.get(("A", "B"), 0) >= 2)
        self.assertTrue(flow.get(("B", "C"), 0) >= 2)
    
    def test_complex_scenario(self):
        """Test a more complex graph with multiple sources and destinations."""
        def capacity_AB(time):
            return 10
        
        def capacity_BC(time):
            return 8
        
        def capacity_BD(time):
            return 5
        
        def capacity_CD(time):
            return 6
        
        def capacity_DE(time):
            return 12
        
        graph = {
            "A": {"B": capacity_AB},
            "B": {"C": capacity_BC, "D": capacity_BD},
            "C": {"D": capacity_CD},
            "D": {"E": capacity_DE},
            "E": {}
        }
        sources = ["A"]
        destinations = ["E"]
        road_closures = [(10, 20, "B", "C")]
        emergency_requests = [(15, "A", "E", 2, ["A", "B", "D", "E"])]
        
        # Before road closure and emergency
        time = 5
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow[("A", "B")], 10)
        self.assertEqual(flow[("B", "C")] + flow[("B", "D")], 10)
        self.assertEqual(flow[("C", "D")] + flow[("B", "D")], flow[("D", "E")])
        
        # During road closure
        time = 15
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        self.assertEqual(flow.get(("B", "C"), 0), 0)  # Road closed
        self.assertTrue(flow.get(("A", "B"), 0) >= 2)  # Emergency vehicles
        self.assertTrue(flow.get(("B", "D"), 0) >= 2)  # Emergency vehicles
        self.assertTrue(flow.get(("D", "E"), 0) >= 2)  # Emergency vehicles
    
    def test_multiple_sources_destinations(self):
        """Test a graph with multiple sources and destinations."""
        def capacity(time):
            return 5
        
        graph = {
            "A": {"C": capacity, "D": capacity},
            "B": {"C": capacity, "D": capacity},
            "C": {"E": capacity},
            "D": {"E": capacity},
            "E": {}
        }
        sources = ["A", "B"]
        destinations = ["E"]
        road_closures = []
        emergency_requests = []
        
        time = 5
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        
        # Check total flow from sources
        total_from_A = flow.get(("A", "C"), 0) + flow.get(("A", "D"), 0)
        total_from_B = flow.get(("B", "C"), 0) + flow.get(("B", "D"), 0)
        self.assertEqual(total_from_A + total_from_B, 10)
        
        # Check total flow to destinations
        total_to_E = flow.get(("C", "E"), 0) + flow.get(("D", "E"), 0)
        self.assertEqual(total_to_E, 10)
    
    def test_flow_conservation(self):
        """Test flow conservation at each intersection."""
        def capacity(time):
            return 5
        
        graph = {
            "A": {"B": capacity, "C": capacity},
            "B": {"D": capacity},
            "C": {"D": capacity},
            "D": {"E": capacity},
            "E": {}
        }
        sources = ["A"]
        destinations = ["E"]
        road_closures = []
        emergency_requests = []
        
        time = 5
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        
        # Check flow conservation at B
        flow_in_B = flow.get(("A", "B"), 0)
        flow_out_B = flow.get(("B", "D"), 0)
        self.assertEqual(flow_in_B, flow_out_B)
        
        # Check flow conservation at C
        flow_in_C = flow.get(("A", "C"), 0)
        flow_out_C = flow.get(("C", "D"), 0)
        self.assertEqual(flow_in_C, flow_out_C)
        
        # Check flow conservation at D
        flow_in_D = flow.get(("B", "D"), 0) + flow.get(("C", "D"), 0)
        flow_out_D = flow.get(("D", "E"), 0)
        self.assertEqual(flow_in_D, flow_out_D)
    
    def test_alternative_paths_with_emergency(self):
        """Test finding alternative paths when emergency vehicles use the main path."""
        def capacity(time):
            return 10
        
        graph = {
            "A": {"B": capacity, "C": capacity},
            "B": {"D": capacity},
            "C": {"D": capacity},
            "D": {"E": capacity},
            "E": {}
        }
        sources = ["A"]
        destinations = ["E"]
        road_closures = []
        emergency_requests = [(5, "A", "E", 8, ["A", "B", "D", "E"])]
        
        time = 5
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        
        # Check emergency path is used
        self.assertTrue(flow.get(("A", "B"), 0) >= 8)
        self.assertTrue(flow.get(("B", "D"), 0) >= 8)
        self.assertTrue(flow.get(("D", "E"), 0) >= 8)
        
        # Check alternative path is used for remaining capacity
        total_flow_to_E = flow.get(("D", "E"), 0)
        self.assertEqual(total_flow_to_E, 10)  # Total capacity of D->E
    
    def test_larger_graph(self):
        """Test with a larger graph to ensure performance."""
        def capacity(time):
            return 5
        
        # Create a larger graph
        graph = {}
        for i in range(100):
            neighbors = {}
            for j in range(i+1, min(i+6, 100)):
                neighbors[str(j)] = capacity
            graph[str(i)] = neighbors
        
        sources = ["0"]
        destinations = ["99"]
        road_closures = [(10, 20, "50", "51")]
        emergency_requests = [(15, "0", "99", 2, ["0", "1", "7", "13", "19", "25", "31", "37", "43", "49", "55", "61", "67", "73", "79", "85", "91", "97", "98", "99"])]
        
        time = 15
        flow = optimize_traffic_flow(graph, sources, destinations, road_closures, emergency_requests, time)
        
        # Check that we get a result (basic performance test)
        self.assertTrue(isinstance(flow, dict))
        
        # Check emergency path is guaranteed
        for i in range(len(emergency_requests[0][4]) - 1):
            src = emergency_requests[0][4][i]
            dst = emergency_requests[0][4][i+1]
            self.assertTrue(flow.get((src, dst), 0) >= emergency_requests[0][3])

if __name__ == "__main__":
    unittest.main()