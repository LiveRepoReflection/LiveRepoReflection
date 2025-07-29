import unittest
from social_distance import analyze_network

class TestSocialDistance(unittest.TestCase):
    def test_direct_connection(self):
        # Graph:
        # 1: {2}
        # 2: {1}
        def get_connections(uid):
            network = {
                1: {2},
                2: {1}
            }
            return network.get(uid, set())
        
        # Expecting a direct edge from 1 to 2: 1 hop.
        result = analyze_network(1, {2}, Q=2, get_connections=get_connections)
        self.assertEqual(result, 1)

    def test_multi_hops(self):
        # Graph:
        # 1: {2, 3}
        # 2: {1, 4}
        # 3: {1, 5}
        # 4: {2, 6}
        # 5: {3, 6}
        # 6: {4, 5}
        def get_connections(uid):
            network = {
                1: {2, 3},
                2: {1, 4},
                3: {1, 5},
                4: {2, 6},
                5: {3, 6},
                6: {4, 5}
            }
            return network.get(uid, set())
        
        # The shortest path from 1 to 6 is either 1->2->4->6 or 1->3->5->6.
        result = analyze_network(1, {6}, Q=10, get_connections=get_connections)
        self.assertEqual(result, 3)

    def test_multiple_targets(self):
        # Graph:
        # 1: {2, 3}
        # 2: {1, 4, 5}
        # 3: {1, 6}
        # 4: {2}
        # 5: {2, 7}
        # 6: {3}
        # 7: {5}
        def get_connections(uid):
            network = {
                1: {2, 3},
                2: {1, 4, 5},
                3: {1, 6},
                4: {2},
                5: {2, 7},
                6: {3},
                7: {5}
            }
            return network.get(uid, set())
        
        # Targets: {4, 7}. The shortest path to 4 is 1->2->4 (2 hops) and to 7 is 1->2->5->7 (3 hops).
        result = analyze_network(1, {4, 7}, Q=10, get_connections=get_connections)
        self.assertEqual(result, 2)

    def test_immediate_target(self):
        # When the starting user is already a target, the distance is 0.
        def get_connections(uid):
            # Graph details are irrelevant in this case.
            return {}
        
        result = analyze_network(5, {5}, Q=1, get_connections=get_connections)
        self.assertEqual(result, 0)

    def test_query_limit(self):
        # Graph:
        # 1: {2}
        # 2: {1, 3}
        # 3: {2, 4}
        # 4: {3}
        def get_connections(uid):
            network = {
                1: {2},
                2: {1, 3},
                3: {2, 4},
                4: {3}
            }
            return network.get(uid, set())
        
        # With Q=2, the available queries will not be enough to reach target 4.
        result = analyze_network(1, {4}, Q=2, get_connections=get_connections)
        self.assertEqual(result, -1)

if __name__ == '__main__':
    unittest.main()