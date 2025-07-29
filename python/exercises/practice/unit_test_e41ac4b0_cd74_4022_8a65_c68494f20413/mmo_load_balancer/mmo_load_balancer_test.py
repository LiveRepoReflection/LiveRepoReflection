import unittest
import time
from mmo_load_balancer import assign_player

class TestMMOLoadBalancer(unittest.TestCase):
    def test_no_server_available(self):
        servers = []
        with self.assertRaises(ValueError):
            assign_player(servers, "zone1")

    def test_zone_affinity(self):
        servers = [
            {
                "id": "server1",
                "cpu": 50,
                "memory": 50,
                "players": 40,
                "zones": ["zoneA"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server2",
                "cpu": 30,
                "memory": 30,
                "players": 30,
                "zones": [],
                "weight": 1.0,
                "active": True
            },
        ]
        # Expect that connection request for zoneA gets assigned to server1 because of zone affinity.
        result = assign_player(servers, "zoneA")
        self.assertEqual(result, "server1")

    def test_overloaded_server(self):
        servers = [
            {
                "id": "server1",
                "cpu": 85,  # Over the assumed CPU threshold of 80%
                "memory": 50,
                "players": 80,
                "zones": ["zoneA"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server2",
                "cpu": 40,
                "memory": 40,
                "players": 30,
                "zones": [],
                "weight": 1.0,
                "active": True
            },
        ]
        # Even though server1 has affinity for zoneA, it is overloaded. The assignment should go to server2.
        result = assign_player(servers, "zoneA")
        self.assertEqual(result, "server2")

    def test_weighted_allocation(self):
        servers = [
            {
                "id": "server1",
                "cpu": 30,
                "memory": 30,
                "players": 20,
                "zones": [],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server2",
                "cpu": 30,
                "memory": 30,
                "players": 20,
                "zones": [],
                "weight": 2.0,
                "active": True
            },
        ]
        count_server1 = 0
        count_server2 = 0
        # Run multiple iterations to statistically observe the weighted bias.
        for _ in range(100):
            result = assign_player(servers, "zoneB")
            if result == "server1":
                count_server1 += 1
            elif result == "server2":
                count_server2 += 1
        # Expect that server2 is selected more frequently than server1 due to its higher weight.
        self.assertGreater(count_server2, count_server1)

    def test_fault_tolerance(self):
        servers = [
            {
                "id": "server1",
                "cpu": 40,
                "memory": 40,
                "players": 20,
                "zones": ["zoneC"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server2",
                "cpu": 40,
                "memory": 40,
                "players": 20,
                "zones": [],
                "weight": 1.0,
                "active": True
            },
        ]
        # Simulate server failure for server1.
        servers[0]["active"] = False
        result = assign_player(servers, "zoneC")
        self.assertEqual(result, "server2")

    def test_hot_zone_detection(self):
        # In this scenario, zoneD is experiencing heavy traffic.
        servers = [
            {
                "id": "server1",
                "cpu": 40,
                "memory": 40,
                "players": 50,  # Higher player count indicating a hot zone
                "zones": ["zoneD"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server2",
                "cpu": 40,
                "memory": 40,
                "players": 20,
                "zones": ["zoneE"],
                "weight": 1.0,
                "active": True
            },
        ]
        # To mitigate hot zones, a new connection for zoneD should be assigned to server2.
        result = assign_player(servers, "zoneD")
        self.assertEqual(result, "server2")

    def test_real_time_performance(self):
        servers = [
            {
                "id": "server1",
                "cpu": 50,
                "memory": 50,
                "players": 30,
                "zones": ["zoneF"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server2",
                "cpu": 50,
                "memory": 50,
                "players": 30,
                "zones": ["zoneG"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server3",
                "cpu": 50,
                "memory": 50,
                "players": 30,
                "zones": ["zoneH"],
                "weight": 1.0,
                "active": True
            },
            {
                "id": "server4",
                "cpu": 50,
                "memory": 50,
                "players": 30,
                "zones": ["zoneI"],
                "weight": 1.0,
                "active": True
            },
        ]
        start = time.time()
        for i in range(10000):
            # Cycle through zones zoneF, zoneG, zoneH, zoneI
            zone = "zone" + chr(70 + (i % 4))
            assign_player(servers, zone)
        duration = time.time() - start
        # Ensure that the performance is acceptable (10000 assignments should complete in under 1 second).
        self.assertLess(duration, 1)

if __name__ == '__main__':
    unittest.main()