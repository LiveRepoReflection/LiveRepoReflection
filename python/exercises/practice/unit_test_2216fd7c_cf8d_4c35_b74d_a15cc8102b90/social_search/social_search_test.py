import unittest
from collections import deque
from social_search import search_social_graph

# A simple Jaccard similarity function for our expected results.
def jaccard_similarity(str1, str2):
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())
    if not set1 and not set2:
        return 1.0
    return float(len(set1.intersection(set2))) / len(set1.union(set2))

class MockNode:
    def __init__(self, node_id, user_profiles=None, neighbor_ids=None, network=None):
        self.id = node_id
        self.user_profiles = user_profiles if user_profiles is not None else {}
        self.neighbor_ids = neighbor_ids if neighbor_ids is not None else []
        self.network = network  # Reference to global network dict (node_id -> MockNode)
        self.message_queue = deque()

    @property
    def neighbors(self):
        # Return list of neighbor node ids.
        return self.neighbor_ids

    def get_user_profile(self, user_id):
        return self.user_profiles.get(user_id, None)

    def send_message(self, destination_node_id, message):
        if self.network and destination_node_id in self.network:
            self.network[destination_node_id].message_queue.append(message)

    def receive_message(self):
        if self.message_queue:
            return self.message_queue.popleft()
        return None

class SocialSearchTest(unittest.TestCase):
    def setUp(self):
        # Build a network of nodes.
        self.network = {}

        # Node A: starting node.
        # Contains two user profiles.
        profiles_A = {
            "A1": "python developer",
            "A2": "data scientist"
        }
        node_A = MockNode("A", profiles_A, neighbor_ids=["B", "C"], network=self.network)
        self.network["A"] = node_A

        # Node B
        profiles_B = {
            "B1": "senior python developer",
            "B2": "java engineer"
        }
        node_B = MockNode("B", profiles_B, neighbor_ids=["D"], network=self.network)
        self.network["B"] = node_B

        # Node C
        profiles_C = {
            "C1": "python developer",
            "C2": "full stack developer"
        }
        node_C = MockNode("C", profiles_C, neighbor_ids=["D"], network=self.network)
        self.network["C"] = node_C

        # Node D - forming a cycle back to A for testing cycles.
        profiles_D = {
            "D1": "python programmer",
            "D2": "python developer expert"
        }
        node_D = MockNode("D", profiles_D, neighbor_ids=["A"], network=self.network)
        self.network["D"] = node_D

    def test_single_node_match(self):
        # Test search on a single node without neighbors.
        # Create an isolated node with one profile that matches exactly.
        isolated_network = {}
        profiles = {"X1": "python developer"}
        node_X = MockNode("X", profiles, neighbor_ids=[], network=isolated_network)
        isolated_network["X"] = node_X

        # With exact match and threshold 1.0, similarity should be 1.0.
        query = "python developer"
        max_hops = 0
        similarity_threshold = 1.0

        result = search_social_graph(node_X, query, max_hops, similarity_threshold)
        # Expect only "X1" with similarity 1.0.
        expected = [("X1", 1.0)]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], expected[0][0])
        self.assertAlmostEqual(result[0][1], expected[0][1], places=4)

    def test_multi_node_with_hops(self):
        # Test search across multiple nodes.
        # Query: "python developer" with threshold 1.0 should only return exact matches.
        starting_node = self.network["A"]
        query = "python developer"
        max_hops = 2
        similarity_threshold = 1.0

        # Expected:
        # Node A: A1 ("python developer") -> similarity 1.0.
        # Node C: C1 ("python developer") -> similarity 1.0.
        # Other profiles do not match exactly.
        expected_ids = set(["A1", "C1"])

        result = search_social_graph(starting_node, query, max_hops, similarity_threshold)
        result_ids = set(uid for uid, score in result)
        self.assertEqual(result_ids, expected_ids)
        # Check that all similarity scores are >= threshold.
        for uid, score in result:
            self.assertGreaterEqual(score, similarity_threshold)
        # Check descending order of similarity scores.
        similarity_scores = [score for uid, score in result]
        self.assertEqual(similarity_scores, sorted(similarity_scores, reverse=True))

    def test_max_hops_zero(self):
        # Test that search respects max_hops = 0 (only the starting node is searched).
        starting_node = self.network["A"]
        query = "python developer"
        max_hops = 0
        similarity_threshold = 1.0

        # Only node A should be searched.
        # Expected: A1 ("python developer") from node A.
        result = search_social_graph(starting_node, query, max_hops, similarity_threshold)
        expected_ids = set(["A1"])
        result_ids = set(uid for uid, score in result)
        self.assertEqual(result_ids, expected_ids)

    def test_no_matches(self):
        # Test when no profiles meet the similarity threshold.
        starting_node = self.network["A"]
        query = "c++ developer"
        max_hops = 2
        similarity_threshold = 0.5

        result = search_social_graph(starting_node, query, max_hops, similarity_threshold)
        self.assertEqual(result, [])

    def test_cycle_handling(self):
        # Test that the algorithm handles cycles without infinite loops.
        # For this, we use the existing network which contains a cycle: D neighbors include A.
        starting_node = self.network["A"]
        query = "python developer"
        max_hops = 3
        similarity_threshold = 1.0

        # Expected should be the same as in test_multi_node_with_hops.
        expected_ids = set(["A1", "C1"])
        result = search_social_graph(starting_node, query, max_hops, similarity_threshold)
        result_ids = set(uid for uid, score in result)
        self.assertEqual(result_ids, expected_ids)
        # Additionally, confirm that no node is processed more than once by comparing
        # count of returned profiles to unique profiles.
        self.assertEqual(len(result_ids), len(result))

if __name__ == '__main__':
    unittest.main()