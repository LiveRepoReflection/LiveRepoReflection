import unittest
from network_risk import analyze_network

class NetworkRiskTest(unittest.TestCase):
    def test_example_case(self):
        # Provided example
        devices = {
            "A": {
                "device_type": "web_server",
                "os_version": "Linux",
                "open_ports": [80, 443],
                "vulnerabilities": [3, 5]
            },
            "B": {
                "device_type": "application_server",
                "os_version": "Windows",
                "open_ports": [8080],
                "vulnerabilities": [7, 2]
            },
            "C": {
                "device_type": "database_server",
                "os_version": "Linux",
                "open_ports": [3306],
                "vulnerabilities": [9]
            },
            "D": {
                "device_type": "workstation",
                "os_version": "Windows",
                "open_ports": [139, 445],
                "vulnerabilities": [1, 4]
            }
        }
        edges = [("A", "B"), ("B", "C"), ("A", "D")]
        entry_point = "A"
        target_devices = ["C", "D"]

        expected_score = 26  # 8 (A) + 9 (B) + 9 (C)
        expected_path = ["A", "B", "C"]

        result = analyze_network(devices, edges, entry_point, target_devices)
        self.assertEqual(result, (expected_score, expected_path))

    def test_no_path(self):
        # Test case when no path exists from entry_point to any target
        devices = {
            "A": {
                "device_type": "router",
                "os_version": "Linux",
                "open_ports": [22],
                "vulnerabilities": [5]
            },
            "B": {
                "device_type": "server",
                "os_version": "Linux",
                "open_ports": [22, 80],
                "vulnerabilities": [3]
            },
            "C": {
                "device_type": "server",
                "os_version": "Linux",
                "open_ports": [80],
                "vulnerabilities": [4]
            }
        }
        edges = [("A", "B")]
        entry_point = "A"
        target_devices = ["C"]

        expected_score = 0
        expected_path = []

        result = analyze_network(devices, edges, entry_point, target_devices)
        self.assertEqual(result, (expected_score, expected_path))

    def test_cycle_in_graph(self):
        # Test a cyclic graph where a simple path should be selected without infinite loops.
        devices = {
            "A": {"device_type": "router", "os_version": "Linux", "open_ports": [22], "vulnerabilities": [3]},
            "B": {"device_type": "switch", "os_version": "Linux", "open_ports": [80], "vulnerabilities": [3]},
            "C": {"device_type": "server", "os_version": "Linux", "open_ports": [443], "vulnerabilities": [5]}
        }
        edges = [("A", "B"), ("B", "C"), ("C", "A")]
        entry_point = "A"
        target_devices = ["C"]

        # Expected path: A -> B -> C  with vulnerability sum = 3 + 3 + 5 = 11
        expected_score = 11
        expected_path = ["A", "B", "C"]

        result = analyze_network(devices, edges, entry_point, target_devices)
        self.assertEqual(result, (expected_score, expected_path))

    def test_tie_break_by_shortest_path(self):
        # Test when multiple paths have the same score but different lengths.
        # In this case, should return the shortest path.
        devices = {
            "A": {"device_type": "gateway", "os_version": "Linux", "open_ports": [80], "vulnerabilities": [10]},
            "B": {"device_type": "server", "os_version": "Windows", "open_ports": [8080], "vulnerabilities": [1]},
            "D": {"device_type": "database", "os_version": "Linux", "open_ports": [3306], "vulnerabilities": [10]},
            "E": {"device_type": "proxy", "os_version": "Linux", "open_ports": [3128], "vulnerabilities": [0]}
        }
        # Two possible paths from A to D:
        # Path1: A -> B -> D: vulnerability sum = 10 + 1 + 10 = 21; length = 3
        # Path2: A -> E -> B -> D: vulnerability sum = 10 + 0 + 1 + 10 = 21; length = 4
        edges = [("A", "B"), ("B", "D"), ("A", "E"), ("E", "B")]
        entry_point = "A"
        target_devices = ["D"]

        expected_score = 21
        expected_path = ["A", "B", "D"]

        result = analyze_network(devices, edges, entry_point, target_devices)
        self.assertEqual(result, (expected_score, expected_path))

    def test_disconnected_components(self):
        # Test graph with multiple disconnected components.
        devices = {
            "A": {"device_type": "gateway", "os_version": "Linux", "open_ports": [443], "vulnerabilities": [2]},
            "B": {"device_type": "server", "os_version": "Windows", "open_ports": [80], "vulnerabilities": [2]},
            "C": {"device_type": "workstation", "os_version": "Windows", "open_ports": [3389], "vulnerabilities": [3]},
            "D": {"device_type": "server", "os_version": "Linux", "open_ports": [22], "vulnerabilities": [4]},
            "E": {"device_type": "database", "os_version": "Linux", "open_ports": [3306], "vulnerabilities": [5]},
            "F": {"device_type": "router", "os_version": "Linux", "open_ports": [161], "vulnerabilities": [1]}
        }
        # Component 1: A -> B -> C
        # Component 2: D -> E
        # Edge from F to C to connect them and provide an alternative path from entry point F.
        edges = [("A", "B"), ("B", "C"), ("D", "E"), ("F", "C")]
        # entry_point is F, target devices are C and E.
        # Possible path from F -> C is direct: sum = 1 + 3 = 4
        # For E, a path F -> C -> (no connection to D/E) so only valid is F -> C if C is target.
        # Since E is not reachable, the best is F -> C.
        entry_point = "F"
        target_devices = ["C", "E"]

        expected_score = 4
        expected_path = ["F", "C"]

        result = analyze_network(devices, edges, entry_point, target_devices)
        self.assertEqual(result, (expected_score, expected_path))

if __name__ == '__main__':
    unittest.main()