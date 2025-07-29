import unittest
from network_segmentation import segment_network

class TestNetworkSegmentation(unittest.TestCase):
    def test_basic_case(self):
        n = 6
        connections = [(0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5), (0, 3)]
        k = 2
        critical_pairs = [(0, 5), (1, 4)]
        min_size = 2
        max_size = 4
        
        result = segment_network(n, connections, k, critical_pairs, min_size, max_size)
        self._validate_result(n, result, k, critical_pairs, min_size, max_size)
        cross_segments = self._count_cross_segments(result, connections)
        self.assertTrue(cross_segments == 1 or cross_segments == 4)

    def test_no_valid_segmentation(self):
        n = 4
        connections = [(0, 1), (1, 2), (2, 3)]
        k = 2
        critical_pairs = [(0, 1), (1, 2), (2, 3)]
        min_size = 2
        max_size = 2
        
        result = segment_network(n, connections, k, critical_pairs, min_size, max_size)
        self.assertIsNone(result)

    def test_larger_network(self):
        n = 10
        connections = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),
                      (0,5),(1,6),(2,7),(3,8),(4,9)]
        k = 3
        critical_pairs = [(0,9),(1,8),(2,7),(3,6),(4,5)]
        min_size = 3
        max_size = 4
        
        result = segment_network(n, connections, k, critical_pairs, min_size, max_size)
        self._validate_result(n, result, k, critical_pairs, min_size, max_size)

    def test_min_max_size_constraints(self):
        n = 8
        connections = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),
                      (0,4),(1,5),(2,6),(3,7)]
        k = 2
        critical_pairs = [(0,7),(1,6),(2,5),(3,4)]
        min_size = 3
        max_size = 5
        
        result = segment_network(n, connections, k, critical_pairs, min_size, max_size)
        self._validate_result(n, result, k, critical_pairs, min_size, max_size)
        for segment in result:
            self.assertTrue(len(segment) >= min_size and len(segment) <= max_size)

    def _validate_result(self, n, result, k, critical_pairs, min_size, max_size):
        if result is None:
            return
            
        self.assertEqual(len(result), k)
        
        # Check all devices are present exactly once
        all_devices = set()
        for segment in result:
            all_devices.update(segment)
        self.assertEqual(len(all_devices), n)
        self.assertEqual(all_devices, set(range(n)))
        
        # Check critical pairs are in different segments
        for a, b in critical_pairs:
            a_segment = None
            b_segment = None
            for segment in result:
                if a in segment:
                    a_segment = segment
                if b in segment:
                    b_segment = segment
            self.assertNotEqual(a_segment, b_segment)
        
        # Check segment size constraints
        for segment in result:
            self.assertTrue(len(segment) >= min_size)
            self.assertTrue(len(segment) <= max_size)

    def _count_cross_segments(self, segments, connections):
        count = 0
        segment_map = {}
        for i, segment in enumerate(segments):
            for device in segment:
                segment_map[device] = i
                
        for u, v in connections:
            if segment_map[u] != segment_map[v]:
                count += 1
        return count

if __name__ == '__main__':
    unittest.main()