import unittest
from network_orchestrator import NetworkOrchestrator

class TestNetworkOrchestrator(unittest.TestCase):
    def setUp(self):
        self.n = 10
        self.orchestrator = NetworkOrchestrator(self.n)

    def test_initial_state(self):
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue
                self.assertFalse(self.orchestrator.sendMessage(i, j, "test"))

    def test_basic_connect_send(self):
        self.orchestrator.connect(0, 1)
        self.assertTrue(self.orchestrator.sendMessage(0, 1, "hello"))
        self.assertTrue(self.orchestrator.sendMessage(1, 0, "world"))

    def test_disconnect(self):
        self.orchestrator.connect(0, 1)
        self.orchestrator.disconnect(0, 1)
        self.assertFalse(self.orchestrator.sendMessage(0, 1, "test"))

    def test_multi_hop_routing(self):
        self.orchestrator.connect(0, 1)
        self.orchestrator.connect(1, 2)
        self.assertTrue(self.orchestrator.sendMessage(0, 2, "multi-hop"))

    def test_self_message(self):
        self.assertTrue(self.orchestrator.sendMessage(0, 0, "self"))

    def test_partitioned_network(self):
        self.orchestrator.connect(0, 1)
        self.orchestrator.connect(2, 3)
        self.assertFalse(self.orchestrator.sendMessage(0, 3, "partitioned"))

    def test_dynamic_topology(self):
        self.orchestrator.connect(0, 1)
        self.orchestrator.connect(1, 2)
        self.orchestrator.disconnect(1, 2)
        self.orchestrator.connect(0, 2)
        self.assertTrue(self.orchestrator.sendMessage(0, 2, "dynamic"))

    def test_duplicate_connections(self):
        self.orchestrator.connect(0, 1)
        self.orchestrator.connect(0, 1)  # duplicate
        self.assertTrue(self.orchestrator.sendMessage(0, 1, "duplicate"))

    def test_nonexistent_disconnect(self):
        self.orchestrator.disconnect(0, 1)  # no connection exists
        self.assertFalse(self.orchestrator.sendMessage(0, 1, "nonexistent"))

    def test_large_network(self):
        large_n = 1000
        large_orchestrator = NetworkOrchestrator(large_n)
        for i in range(large_n - 1):
            large_orchestrator.connect(i, i + 1)
        self.assertTrue(large_orchestrator.sendMessage(0, large_n - 1, "large"))

    def test_rapid_connect_disconnect(self):
        for _ in range(100):
            self.orchestrator.connect(0, 1)
            self.orchestrator.disconnect(0, 1)
        self.assertFalse(self.orchestrator.sendMessage(0, 1, "rapid"))

    def test_multiple_routes(self):
        self.orchestrator.connect(0, 1)
        self.orchestrator.connect(0, 2)
        self.orchestrator.connect(1, 3)
        self.orchestrator.connect(2, 3)
        self.assertTrue(self.orchestrator.sendMessage(0, 3, "multiple routes"))

    def test_connection_to_self(self):
        self.orchestrator.connect(0, 0)  # should be no-op
        self.assertTrue(self.orchestrator.sendMessage(0, 0, "self connect"))

if __name__ == '__main__':
    unittest.main()