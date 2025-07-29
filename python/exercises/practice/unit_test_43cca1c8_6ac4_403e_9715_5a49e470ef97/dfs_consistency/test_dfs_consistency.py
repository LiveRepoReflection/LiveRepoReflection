import unittest
from unittest.mock import patch, MagicMock
from dfs_consistency.dfs_consistency import check_consistency

class TestDFSConsistency(unittest.TestCase):
    def setUp(self):
        self.nodes = ["node1", "node2", "node3"]
        
    @patch('dfs_consistency.dfs_consistency.get_chunk_metadata')
    def test_no_inconsistencies(self, mock_get_metadata):
        mock_get_metadata.side_effect = [
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}],
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}],
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}]
        ]
        result = check_consistency(self.nodes)
        self.assertEqual(result, [])

    @patch('dfs_consistency.dfs_consistency.get_chunk_metadata')
    def test_version_mismatch(self, mock_get_metadata):
        mock_get_metadata.side_effect = [
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}],
            [{'chunk_id': 'chunk1', 'version': 2, 'size': 1024}],
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}]
        ]
        result = check_consistency(self.nodes)
        expected = [{
            'chunk_id': 'chunk1',
            'inconsistent_nodes': [
                ('node1', {'chunk_id': 'chunk1', 'version': 1, 'size': 1024}),
                ('node2', {'chunk_id': 'chunk1', 'version': 2, 'size': 1024}),
                ('node3', {'chunk_id': 'chunk1', 'version': 1, 'size': 1024})
            ],
            'reason': 'version mismatch'
        }]
        self.assertEqual(result, expected)

    @patch('dfs_consistency.dfs_consistency.get_chunk_metadata')
    def test_size_mismatch(self, mock_get_metadata):
        mock_get_metadata.side_effect = [
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}],
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 2048}],
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}]
        ]
        result = check_consistency(self.nodes)
        expected = [{
            'chunk_id': 'chunk1',
            'inconsistent_nodes': [
                ('node1', {'chunk_id': 'chunk1', 'version': 1, 'size': 1024}),
                ('node2', {'chunk_id': 'chunk1', 'version': 1, 'size': 2048}),
                ('node3', {'chunk_id': 'chunk1', 'version': 1, 'size': 1024})
            ],
            'reason': 'size mismatch'
        }]
        self.assertEqual(result, expected)

    @patch('dfs_consistency.dfs_consistency.get_chunk_metadata')
    def test_node_failure(self, mock_get_metadata):
        mock_get_metadata.side_effect = [
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}],
            Exception("Connection error"),
            [{'chunk_id': 'chunk1', 'version': 1, 'size': 1024}]
        ]
        result = check_consistency(self.nodes)
        self.assertEqual(result, [])

    @patch('dfs_consistency.dfs_consistency.get_chunk_metadata')
    def test_multiple_inconsistencies(self, mock_get_metadata):
        mock_get_metadata.side_effect = [
            [
                {'chunk_id': 'chunk1', 'version': 1, 'size': 1024},
                {'chunk_id': 'chunk2', 'version': 1, 'size': 2048}
            ],
            [
                {'chunk_id': 'chunk1', 'version': 2, 'size': 1024},
                {'chunk_id': 'chunk2', 'version': 1, 'size': 4096}
            ],
            [
                {'chunk_id': 'chunk1', 'version': 1, 'size': 1024},
                {'chunk_id': 'chunk2', 'version': 1, 'size': 2048}
            ]
        ]
        result = check_consistency(self.nodes)
        expected = [
            {
                'chunk_id': 'chunk1',
                'inconsistent_nodes': [
                    ('node1', {'chunk_id': 'chunk1', 'version': 1, 'size': 1024}),
                    ('node2', {'chunk_id': 'chunk1', 'version': 2, 'size': 1024}),
                    ('node3', {'chunk_id': 'chunk1', 'version': 1, 'size': 1024})
                ],
                'reason': 'version mismatch'
            },
            {
                'chunk_id': 'chunk2',
                'inconsistent_nodes': [
                    ('node1', {'chunk_id': 'chunk2', 'version': 1, 'size': 2048}),
                    ('node2', {'chunk_id': 'chunk2', 'version': 1, 'size': 4096}),
                    ('node3', {'chunk_id': 'chunk2', 'version': 1, 'size': 2048})
                ],
                'reason': 'size mismatch'
            }
        ]
        self.assertEqual(len(result), 2)
        self.assertIn(expected[0], result)
        self.assertIn(expected[1], result)

    @patch('dfs_consistency.dfs_consistency.get_chunk_metadata')
    def test_empty_node_list(self, mock_get_metadata):
        result = check_consistency([])
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()