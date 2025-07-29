import unittest
from copy import deepcopy
from autonomous_routing.routing import RoutingSystem

class TestRoutingSystem(unittest.TestCase):
    def setUp(self):
        # Initialize a new RoutingSystem for each test.
        self.routing_system = RoutingSystem()

    def test_static_routing(self):
        # Create a simple network:
        # 1 -> 2 (latency 10, bandwidth 100)
        # 2 -> 3 (latency 10, bandwidth 50)
        # 1 -> 3 (latency 25, bandwidth 100)
        for node in [1, 2, 3]:
            self.routing_system.add_node(node)
        self.routing_system.add_edge(1, 2, latency=10, bandwidth=100)
        self.routing_system.add_edge(2, 3, latency=10, bandwidth=50)
        self.routing_system.add_edge(1, 3, latency=25, bandwidth=100)

        self.routing_system.compute_routing_tables()

        # For node 1, expect the best route to 3 to be via node 2,
        # with total latency 20 and available bandwidth equal to the minimum along the path (i.e. 50).
        rt1 = self.routing_system.get_routing_table(1)
        self.assertIn(3, rt1)
        route_to_3 = rt1[3]
        self.assertEqual(route_to_3["next_hop"], 2)
        self.assertEqual(route_to_3["path"], [1, 2, 3])
        self.assertEqual(route_to_3["latency"], 20)
        self.assertEqual(route_to_3["bandwidth"], 50)

        # For node 2, best route to 3 should be direct.
        rt2 = self.routing_system.get_routing_table(2)
        self.assertIn(3, rt2)
        route_2_to_3 = rt2[3]
        self.assertEqual(route_2_to_3["next_hop"], 3)
        self.assertEqual(route_2_to_3["path"], [2, 3])
        self.assertEqual(route_2_to_3["latency"], 10)
        self.assertEqual(route_2_to_3["bandwidth"], 50)

    def test_dynamic_update(self):
        # Setup a network with two routes from 1 to 3.
        for node in [1, 2, 3]:
            self.routing_system.add_node(node)
        # Two routes: 1->2->3 and 1->3 direct.
        self.routing_system.add_edge(1, 2, latency=10, bandwidth=100)
        self.routing_system.add_edge(2, 3, latency=10, bandwidth=50)
        self.routing_system.add_edge(1, 3, latency=25, bandwidth=100)
        self.routing_system.compute_routing_tables()

        # Initially, the best route from 1 to 3 is expected to be 1->2->3.
        rt1 = self.routing_system.get_routing_table(1)
        self.assertIn(3, rt1)
        self.assertEqual(rt1[3]["next_hop"], 2)
        self.assertEqual(rt1[3]["latency"], 20)

        # Now update the direct edge with lower latency.
        self.routing_system.simulate_edge_failure(1, 3)
        self.routing_system.add_edge(1, 3, latency=5, bandwidth=80)
        self.routing_system.compute_routing_tables()

        rt1_updated = self.routing_system.get_routing_table(1)
        self.assertIn(3, rt1_updated)
        # Expect now the direct route 1->3 is chosen.
        self.assertEqual(rt1_updated[3]["next_hop"], 3)
        self.assertEqual(rt1_updated[3]["path"], [1, 3])
        self.assertEqual(rt1_updated[3]["latency"], 5)
        self.assertEqual(rt1_updated[3]["bandwidth"], 80)

    def test_node_failure(self):
        # Create a network:
        # 1 -> 2 (latency 10, bandwidth 100)
        # 2 -> 3 (latency 10, bandwidth 50)
        for node in [1, 2, 3]:
            self.routing_system.add_node(node)
        self.routing_system.add_edge(1, 2, latency=10, bandwidth=100)
        self.routing_system.add_edge(2, 3, latency=10, bandwidth=50)
        self.routing_system.compute_routing_tables()

        # Before failure, node 1 can reach node 3.
        rt1 = self.routing_system.get_routing_table(1)
        self.assertIn(3, rt1)

        # Simulate failure of node 2.
        self.routing_system.simulate_node_failure(2)
        self.routing_system.compute_routing_tables()

        # After node 2 fails, node 1 should not have a route to node 3.
        rt1_after = self.routing_system.get_routing_table(1)
        self.assertNotIn(3, rt1_after)

    def test_loop_prevention(self):
        # Create a cyclic network:
        # 1 -> 2, 2 -> 3, 3 -> 1, and also 1 -> 4, 2 -> 4, 3 -> 4
        for node in [1, 2, 3, 4]:
            self.routing_system.add_node(node)
        self.routing_system.add_edge(1, 2, latency=5, bandwidth=100)
        self.routing_system.add_edge(2, 3, latency=5, bandwidth=100)
        self.routing_system.add_edge(3, 1, latency=5, bandwidth=100)
        self.routing_system.add_edge(1, 4, latency=15, bandwidth=90)
        self.routing_system.add_edge(2, 4, latency=15, bandwidth=90)
        self.routing_system.add_edge(3, 4, latency=15, bandwidth=90)
        self.routing_system.compute_routing_tables()

        # For each node, verify that the routing path to node 4 does not contain any cycles.
        for node in [1, 2, 3]:
            rt = self.routing_system.get_routing_table(node)
            self.assertIn(4, rt)
            path = rt[4]["path"]
            # Check that the path does not contain duplicate nodes.
            self.assertEqual(len(path), len(set(path)))
            self.assertEqual(path[0], node)
            self.assertEqual(path[-1], 4)

    def test_tie_breaking(self):
        # Setup a network with two equally optimal paths from 1 to 4:
        # Path A: 1 -> 2 -> 4 (latency 10+10, bandwidth min(100,80)=80)
        # Path B: 1 -> 3 -> 4 (latency 10+10, bandwidth min(100,80)=80)
        for node in [1, 2, 3, 4]:
            self.routing_system.add_node(node)
        self.routing_system.add_edge(1, 2, latency=10, bandwidth=100)
        self.routing_system.add_edge(2, 4, latency=10, bandwidth=80)
        self.routing_system.add_edge(1, 3, latency=10, bandwidth=100)
        self.routing_system.add_edge(3, 4, latency=10, bandwidth=80)
        self.routing_system.compute_routing_tables()

        rt1 = self.routing_system.get_routing_table(1)
        self.assertIn(4, rt1)
        route = rt1[4]
        # Deterministic tie-breaking should select one of the paths consistently.
        # Assume that lower next_hop id is chosen: between 2 and 3, choose 2.
        self.assertEqual(route["next_hop"], 2)
        self.assertEqual(route["path"], [1, 2, 4])
        self.assertEqual(route["latency"], 20)
        self.assertEqual(route["bandwidth"], 80)

    def test_routing_convergence(self):
        # Create a slightly larger network
        nodes = range(1, 8)
        for node in nodes:
            self.routing_system.add_node(node)
        # Construct a network which has multiple paths:
        # 1 -> 2, 1 -> 3; 2 -> 4; 3 -> 4; 4 -> 5; 5 -> 6; 5 -> 7; 6 -> 7; 7 -> 1 (cycle)
        self.routing_system.add_edge(1, 2, latency=5, bandwidth=100)
        self.routing_system.add_edge(1, 3, latency=5, bandwidth=100)
        self.routing_system.add_edge(2, 4, latency=10, bandwidth=90)
        self.routing_system.add_edge(3, 4, latency=10, bandwidth=90)
        self.routing_system.add_edge(4, 5, latency=5, bandwidth=80)
        self.routing_system.add_edge(5, 6, latency=10, bandwidth=70)
        self.routing_system.add_edge(5, 7, latency=10, bandwidth=70)
        self.routing_system.add_edge(6, 7, latency=5, bandwidth=70)
        self.routing_system.add_edge(7, 1, latency=20, bandwidth=60)

        # Run multiple rounds of routing computation to simulate convergence.
        self.routing_system.compute_routing_tables()
        routing_tables_first = {node: deepcopy(self.routing_system.get_routing_table(node)) for node in nodes}

        # Run computation a second time.
        self.routing_system.compute_routing_tables()
        routing_tables_second = {node: self.routing_system.get_routing_table(node) for node in nodes}

        # The routing tables should have converged (remain stable between iterations).
        self.assertEqual(routing_tables_first, routing_tables_second)

if __name__ == '__main__':
    unittest.main()