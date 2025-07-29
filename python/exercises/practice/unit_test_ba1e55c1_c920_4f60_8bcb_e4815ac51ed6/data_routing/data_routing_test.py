import unittest
from data_routing import RoutingSystem

class RoutingSystemTests(unittest.TestCase):
    def setUp(self):
        self.system = RoutingSystem()

    def test_empty_rules(self):
        # When no routing rules are present, the system should return an empty set for any sensor.
        self.system.update_routing_rules([])
        for sensor in range(10):
            self.assertEqual(self.system.route_data(sensor), set())

    def test_single_rule(self):
        # Single rule: sensors 1 and 2 should route to processing center 10.
        rules = [({1, 2}, {10})]
        self.system.update_routing_rules(rules)
        self.assertEqual(self.system.route_data(1), {10})
        self.assertEqual(self.system.route_data(2), {10})
        self.assertEqual(self.system.route_data(3), set())

    def test_multiple_rules_non_overlapping(self):
        # Two non-overlapping rules.
        rules = [
            ({1, 2}, {10}),
            ({3}, {11, 12})
        ]
        self.system.update_routing_rules(rules)
        self.assertEqual(self.system.route_data(1), {10})
        self.assertEqual(self.system.route_data(2), {10})
        self.assertEqual(self.system.route_data(3), {11, 12})
        self.assertEqual(self.system.route_data(4), set())

    def test_multiple_rules_overlapping(self):
        # Overlapping rules: sensor 3 appears in multiple conditions.
        rules = [
            ({1, 2, 3}, {10}),
            ({2, 3, 4}, {11}),
            ({3, 5}, {12})
        ]
        self.system.update_routing_rules(rules)
        self.assertEqual(self.system.route_data(3), {10, 11, 12})
        self.assertEqual(self.system.route_data(2), {10, 11})
        self.assertEqual(self.system.route_data(1), {10})
        self.assertEqual(self.system.route_data(4), {11})
        self.assertEqual(self.system.route_data(5), {12})
        self.assertEqual(self.system.route_data(6), set())

    def test_rule_override(self):
        # Test that new updates completely override previous routing rules.
        rules1 = [
            ({1, 2}, {10}),
            ({2}, {11})
        ]
        self.system.update_routing_rules(rules1)
        self.assertEqual(self.system.route_data(2), {10, 11})
        # Override with a different set of rules.
        rules2 = [
            ({2}, {12}),
            ({3}, {13})
        ]
        self.system.update_routing_rules(rules2)
        self.assertEqual(self.system.route_data(2), {12})
        self.assertEqual(self.system.route_data(3), {13})
        self.assertEqual(self.system.route_data(1), set())

    def test_large_input(self):
        # Simulate a large input where many sensors share the same processing centers.
        sensors = set(range(1000))
        centers = set(range(1000, 1050))
        rules = [(sensors, centers)]
        self.system.update_routing_rules(rules)
        for s in [0, 500, 999]:
            self.assertEqual(self.system.route_data(s), centers)
        # Test a sensor not in the specified range.
        self.assertEqual(self.system.route_data(1001), set())

    def test_disjoint_sensor_sets(self):
        # Test disjoint sensor groups routing to different centers.
        rules = [
            ({0, 2, 4, 6}, {100}),
            ({1, 3, 5, 7}, {200})
        ]
        self.system.update_routing_rules(rules)
        self.assertEqual(self.system.route_data(0), {100})
        self.assertEqual(self.system.route_data(1), {200})
        self.assertEqual(self.system.route_data(2), {100})
        self.assertEqual(self.system.route_data(3), {200})
        self.assertEqual(self.system.route_data(8), set())

if __name__ == "__main__":
    unittest.main()