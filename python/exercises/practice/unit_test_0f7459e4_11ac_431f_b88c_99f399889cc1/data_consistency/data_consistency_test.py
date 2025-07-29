import unittest
from data_consistency import find_inconsistencies


class DataConsistencyTest(unittest.TestCase):
    def test_simple_example(self):
        data = [
            {0: 1, 1: 2, 2: 3},  # Node 0
            {0: 1, 1: 3},       # Node 1
            {1: 2, 2: 4}        # Node 2
        ]
        
        # Ensure the result contains the expected inconsistencies
        result = sorted(find_inconsistencies(data), key=lambda x: x[0])
        expected = sorted([(1, [0, 1, 2], [2, 3, 2]), (2, [0, 2], [3, 4])], key=lambda x: x[0])
        
        self.assertEqual(len(result), len(expected))
        
        for i in range(len(result)):
            self.assertEqual(result[i][0], expected[i][0])  # Chunk index
            
            # Check that node_ids and version_numbers correspond correctly
            node_version_pairs = sorted(zip(result[i][1], result[i][2]))
            expected_pairs = sorted(zip(expected[i][1], expected[i][2]))
            self.assertEqual(node_version_pairs, expected_pairs)
    
    def test_no_inconsistencies(self):
        data = [
            {0: 1, 1: 2, 2: 3},
            {0: 1, 1: 2},
            {1: 2, 2: 3}
        ]
        self.assertEqual(find_inconsistencies(data), [])
    
    def test_all_nodes_have_inconsistencies(self):
        data = [
            {0: 1, 1: 2, 2: 3},
            {0: 2, 1: 3, 2: 4},
            {0: 3, 1: 4, 2: 5}
        ]
        
        result = sorted(find_inconsistencies(data), key=lambda x: x[0])
        
        # Verify each chunk has inconsistencies
        self.assertEqual(len(result), 3)
        
        # Check chunk 0
        self.assertEqual(result[0][0], 0)
        node_version_pairs_0 = sorted(zip(result[0][1], result[0][2]))
        self.assertEqual(node_version_pairs_0, [(0, 1), (1, 2), (2, 3)])
        
        # Check chunk 1
        self.assertEqual(result[1][0], 1)
        node_version_pairs_1 = sorted(zip(result[1][1], result[1][2]))
        self.assertEqual(node_version_pairs_1, [(0, 2), (1, 3), (2, 4)])
        
        # Check chunk 2
        self.assertEqual(result[2][0], 2)
        node_version_pairs_2 = sorted(zip(result[2][1], result[2][2]))
        self.assertEqual(node_version_pairs_2, [(0, 3), (1, 4), (2, 5)])
    
    def test_single_node_with_chunk(self):
        data = [
            {0: 1},
            {},
            {}
        ]
        # No inconsistencies as each chunk is only on one node
        self.assertEqual(find_inconsistencies(data), [])
    
    def test_empty_nodes(self):
        data = [{}, {}, {}]
        self.assertEqual(find_inconsistencies(data), [])
    
    def test_large_version_numbers(self):
        data = [
            {0: 1000000000},
            {0: 1000000001}
        ]
        result = find_inconsistencies(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 0)  # Chunk index
        node_version_pairs = sorted(zip(result[0][1], result[0][2]))
        self.assertEqual(node_version_pairs, [(0, 1000000000), (1, 1000000001)])
    
    def test_multiple_chunks_some_inconsistent(self):
        data = [
            {0: 1, 1: 2, 2: 3, 3: 4, 4: 5},
            {0: 1, 1: 2, 2: 3, 3: 4, 4: 6},
            {0: 1, 1: 2, 2: 3, 3: 5, 4: 7}
        ]
        
        result = sorted(find_inconsistencies(data), key=lambda x: x[0])
        
        self.assertEqual(len(result), 2)
        
        # Check chunk 3
        self.assertEqual(result[0][0], 3)
        node_version_pairs_3 = sorted(zip(result[0][1], result[0][2]))
        self.assertEqual(node_version_pairs_3, [(0, 4), (1, 4), (2, 5)])
        
        # Check chunk 4
        self.assertEqual(result[1][0], 4)
        node_version_pairs_4 = sorted(zip(result[1][1], result[1][2]))
        self.assertEqual(node_version_pairs_4, [(0, 5), (1, 6), (2, 7)])
    
    def test_many_nodes(self):
        # Create 100 nodes where node i has chunk 0 with version i
        data = [{0: i} for i in range(100)]
        
        result = find_inconsistencies(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 0)  # Chunk index
        self.assertEqual(len(result[0][1]), 100)  # All nodes should be listed
        
        # Verify the version numbers match the node IDs (since we set version i for node i)
        node_version_pairs = sorted(zip(result[0][1], result[0][2]))
        self.assertEqual(node_version_pairs, [(i, i) for i in range(100)])
    
    def test_sparse_chunks(self):
        data = [
            {0: 1, 10: 1, 20: 1},
            {0: 1, 10: 2, 20: 1},
            {0: 1, 10: 3, 20: 1}
        ]
        
        result = sorted(find_inconsistencies(data), key=lambda x: x[0])
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 10)  # Chunk index
        node_version_pairs = sorted(zip(result[0][1], result[0][2]))
        self.assertEqual(node_version_pairs, [(0, 1), (1, 2), (2, 3)])
        
    def test_invalid_input_handling(self):
        # Test with non-dictionary node data
        try:
            find_inconsistencies(["not a dict", {}, {}])
            self.fail("Expected exception was not raised")
        except (TypeError, ValueError):
            # Either exception is acceptable
            pass
        
        # Test with non-list input
        try:
            find_inconsistencies("not a list")
            self.fail("Expected exception was not raised")
        except (TypeError, ValueError):
            pass
        
        # Test with dictionary containing non-integer keys or values
        try:
            find_inconsistencies([{0: 1, "string_key": 2}, {0: 1}])
            self.fail("Expected exception was not raised")
        except (TypeError, ValueError):
            pass
        
        try:
            find_inconsistencies([{0: "string_value"}, {0: 1}])
            self.fail("Expected exception was not raised")
        except (TypeError, ValueError):
            pass


if __name__ == '__main__':
    unittest.main()