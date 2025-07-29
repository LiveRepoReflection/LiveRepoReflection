import unittest
from service_network import min_communication_cost

class TestServiceNetwork(unittest.TestCase):
    def test_no_dependency(self):
        # Single service with no dependency; no messaging required; expected cost 0.
        N = 1
        subscriptions = [
            []  # Service 0 subscribes to nothing.
        ]
        publications = [
            []  # Service 0 publishes nothing.
        ]
        request_dependencies = [
            []  # No dependencies.
        ]
        topic_costs = {}
        self.assertEqual(min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs), 0)

    def test_direct_dependency(self):
        # Two services: Service1 depends on Service0.
        N = 2
        subscriptions = [
            [],        # Service 0 has no subscriptions.
            [10]       # Service 1 subscribes to topic 10.
        ]
        publications = [
            [10],      # Service 0 publishes to topic 10.
            []         # Service 1 publishes nothing.
        ]
        request_dependencies = [
            [],        # Service 0 has no dependency.
            [0]        # Service 1 depends on Service0.
        ]
        topic_costs = {10: 5}
        self.assertEqual(min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs), 5)

    def test_transitive_dependency(self):
        # Three services in a chain: Service1 depends on Service0; Service2 depends on Service1.
        N = 3
        subscriptions = [
            [],        # Service 0
            [1],       # Service 1 subscribes to topic 1.
            [2]        # Service 2 subscribes to topic 2.
        ]
        publications = [
            [1],       # Service 0 publishes to topic 1.
            [2],       # Service 1 publishes to topic 2.
            []         # Service 2 publishes nothing.
        ]
        request_dependencies = [
            [],
            [0],
            [1]
        ]
        topic_costs = {1: 3, 2: 4}
        # Expected cost: topic 1 (cost=3) + topic 2 (cost=4) = 7.
        self.assertEqual(min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs), 7)

    def test_cyclic_dependency_with_choice(self):
        # Two services with cyclic dependency. Both services can use either topic 2 or topic 4.
        # Optimal solution is to use topic 4 (cost = 5) for both directions.
        N = 2
        subscriptions = [
            [2, 4],  # Service 0 subscribes to topics 2 and 4.
            [2, 4]   # Service 1 subscribes to topics 2 and 4.
        ]
        publications = [
            [2, 4],  # Service 0 publishes topics 2 and 4.
            [2, 4]   # Service 1 publishes topics 2 and 4.
        ]
        request_dependencies = [
            [1],  # Service 0 depends on Service 1.
            [0]   # Service 1 depends on Service 0.
        ]
        topic_costs = {2: 10, 4: 5}
        self.assertEqual(min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs), 5)

    def test_unreachable_dependency(self):
        # Two services where the dependency cannot be satisfied because there is no publishing or subscribing channel.
        N = 2
        subscriptions = [
            [1],  # Service 0 subscribes to topic 1.
            []    # Service 1 subscribes to nothing.
        ]
        publications = [
            [],   # Service 0 publishes nothing.
            []    # Service 1 publishes nothing.
        ]
        request_dependencies = [
            [],
            [0]   # Service 1 depends on Service 0.
        ]
        topic_costs = {1: 5}
        self.assertEqual(min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs), -1)

    def test_complex_network(self):
        # A more complex network with 4 services in a chain.
        # Service1 depends on Service0, Service2 depends on Service1, Service3 depends on Service2.
        # Multiple topics are available; select the cheapest valid path.
        N = 4
        subscriptions = [
            [10],         # Service 0 subscribes to topic 10.
            [10, 20],     # Service 1 subscribes to topics 10 and 20.
            [20, 30],     # Service 2 subscribes to topics 20 and 30.
            [30, 40]      # Service 3 subscribes to topics 30 and 40.
        ]
        publications = [
            [10, 40],     # Service 0 publishes topics 10 and 40.
            [20],         # Service 1 publishes topic 20.
            [30],         # Service 2 publishes topic 30.
            [40]          # Service 3 publishes topic 40.
        ]
        request_dependencies = [
            [],
            [0],   # Service 1 depends on Service 0.
            [1],   # Service 2 depends on Service 1.
            [2]    # Service 3 depends on Service 2.
        ]
        topic_costs = {10: 5, 20: 3, 30: 4, 40: 2}
        # Expected cost:
        # For dependency (1->0): topic10 (cost=5)
        # For dependency (2->1): topic20 (cost=3)
        # For dependency (3->2): topic30 (cost=4)
        # Total = 5 + 3 + 4 = 12.
        self.assertEqual(min_communication_cost(N, subscriptions, publications, request_dependencies, topic_costs), 12)

if __name__ == '__main__':
    unittest.main()