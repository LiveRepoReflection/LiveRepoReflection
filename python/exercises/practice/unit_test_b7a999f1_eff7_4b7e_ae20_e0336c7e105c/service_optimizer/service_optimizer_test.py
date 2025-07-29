import unittest
from service_optimizer import optimize_communication

class ServiceOptimizerTest(unittest.TestCase):
    def test_basic_example(self):
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": []
        }
        L = {
            ("A", "B"): 10,
            ("A", "C"): 15,
            ("B", "D"): 20,
            ("C", "D"): 25
        }
        critical_pairs = {("A", "D")}
        C = {"B": 5, "C": 7, "D": 3}
        r = {"B": 6, "C": 8, "D": 4}
        B = 10
        R = 1
        p = 0.5
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        # Verify cache placement doesn't exceed budget
        self.assertLessEqual(sum(C[service] for service in cache_placement), B)
        
        # Verify replication doesn't exceed limit
        self.assertLessEqual(len(replication_placement), R)
        
        # Verify all services in cache placement are in the graph
        for service in cache_placement:
            self.assertIn(service, graph)
            
        # Verify all services in replication placement are in the graph
        for service in replication_placement:
            self.assertIn(service, graph)

    def test_single_path(self):
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["D"],
            "D": []
        }
        L = {
            ("A", "B"): 5,
            ("B", "C"): 10,
            ("C", "D"): 15
        }
        critical_pairs = {("A", "D")}
        C = {"A": 3, "B": 4, "C": 5, "D": 6}
        r = {"A": 4, "B": 5, "C": 6, "D": 7}
        B = 8
        R = 1
        p = 0.6
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        self.assertLessEqual(sum(C[service] for service in cache_placement), B)
        self.assertLessEqual(len(replication_placement), R)

    def test_complex_graph(self):
        graph = {
            "S1": ["S2", "S3", "S4"],
            "S2": ["S5", "S6"],
            "S3": ["S6", "S7"],
            "S4": ["S7", "S8"],
            "S5": ["S9"],
            "S6": ["S9"],
            "S7": ["S10"],
            "S8": ["S10"],
            "S9": ["S11"],
            "S10": ["S11"],
            "S11": []
        }
        L = {
            ("S1", "S2"): 5, ("S1", "S3"): 7, ("S1", "S4"): 6,
            ("S2", "S5"): 8, ("S2", "S6"): 9,
            ("S3", "S6"): 10, ("S3", "S7"): 12,
            ("S4", "S7"): 11, ("S4", "S8"): 14,
            ("S5", "S9"): 15, ("S6", "S9"): 16,
            ("S7", "S10"): 17, ("S8", "S10"): 18,
            ("S9", "S11"): 20, ("S10", "S11"): 22
        }
        critical_pairs = {("S1", "S11")}
        C = {name: (i+1)*2 for i, name in enumerate(graph.keys())}
        r = {name: (i+1)*3 for i, name in enumerate(graph.keys())}
        B = 30
        R = 3
        p = 0.7
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        self.assertLessEqual(sum(C[service] for service in cache_placement), B)
        self.assertLessEqual(len(replication_placement), R)

    def test_multiple_critical_pairs(self):
        graph = {
            "A": ["B", "C"],
            "B": ["D", "E"],
            "C": ["E", "F"],
            "D": ["G"],
            "E": ["G"],
            "F": ["G"],
            "G": []
        }
        L = {
            ("A", "B"): 5, ("A", "C"): 7,
            ("B", "D"): 10, ("B", "E"): 12,
            ("C", "E"): 8, ("C", "F"): 9,
            ("D", "G"): 15, ("E", "G"): 20,
            ("F", "G"): 18
        }
        critical_pairs = {("A", "G"), ("B", "G"), ("C", "G")}
        C = {"A": 3, "B": 4, "C": 5, "D": 6, "E": 7, "F": 8, "G": 9}
        r = {"A": 4, "B": 6, "C": 8, "D": 10, "E": 12, "F": 14, "G": 16}
        B = 20
        R = 2
        p = 0.5
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        self.assertLessEqual(sum(C[service] for service in cache_placement), B)
        self.assertLessEqual(len(replication_placement), R)

    def test_no_budget(self):
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": []
        }
        L = {
            ("A", "B"): 10,
            ("B", "C"): 15
        }
        critical_pairs = {("A", "C")}
        C = {"A": 5, "B": 7, "C": 9}
        r = {"A": 6, "B": 8, "C": 10}
        B = 0  # No budget for cache placement
        R = 0  # No replications allowed
        p = 0.4
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        self.assertEqual(len(cache_placement), 0)
        self.assertEqual(len(replication_placement), 0)

    def test_cyclic_graph(self):
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": ["D"],
            "D": ["A"]  # Creating a cycle A->B->C->D->A
        }
        L = {
            ("A", "B"): 5,
            ("B", "C"): 10,
            ("C", "D"): 15,
            ("D", "A"): 20
        }
        critical_pairs = {("A", "C"), ("B", "D")}
        C = {"A": 3, "B": 4, "C": 5, "D": 6}
        r = {"A": 4, "B": 5, "C": 6, "D": 7}
        B = 10
        R = 1
        p = 0.5
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        self.assertLessEqual(sum(C[service] for service in cache_placement), B)
        self.assertLessEqual(len(replication_placement), R)

    def test_full_budget_usage(self):
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": []
        }
        L = {
            ("A", "B"): 10,
            ("A", "C"): 15,
            ("B", "D"): 20,
            ("C", "D"): 25
        }
        critical_pairs = {("A", "D")}
        C = {"B": 5, "C": 7, "D": 8}
        r = {"B": 6, "C": 8, "D": 10}
        B = 12
        R = 1
        p = 0.5
        
        cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
        
        # Not all budgets need to be used, but the algorithm should make good use of them
        self.assertLessEqual(sum(C[service] for service in cache_placement), B)
        self.assertLessEqual(len(replication_placement), R)

if __name__ == '__main__':
    unittest.main()