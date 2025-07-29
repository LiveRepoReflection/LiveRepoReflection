import unittest
from file_consistency import are_chunks_consistent

class FileConsistencyTest(unittest.TestCase):
    def test_all_consistent(self):
        N = 3
        files = ["file1", "file2"]
        chunk_map = {
            "file1": ["chunk1", "chunk2"],
            "file2": ["chunk3"]
        }
        node_data = [
            {
                "chunk1": b"data1",
                "chunk2": b"data2",
                "chunk3": b"data3"
            },
            {
                "chunk1": b"data1",
                "chunk2": b"data2",
                "chunk3": b"data3"
            },
            {
                "chunk1": None,
                "chunk2": b"data2",
                "chunk3": None
            }
        ]
        self.assertTrue(are_chunks_consistent(N, files, chunk_map, node_data))

    def test_inconsistent_chunk(self):
        N = 2
        files = ["file1"]
        chunk_map = {"file1": ["chunk1"]}
        node_data = [
            {"chunk1": b"alpha"},
            {"chunk1": b"beta"}
        ]
        self.assertFalse(are_chunks_consistent(N, files, chunk_map, node_data))

    def test_missing_chunks_consistent(self):
        N = 3
        files = ["file1"]
        chunk_map = {"file1": ["chunk1"]}
        node_data = [
            {"chunk1": None},
            {"chunk1": None},
            {"chunk1": None}
        ]
        self.assertTrue(are_chunks_consistent(N, files, chunk_map, node_data))

    def test_empty_byte_string_consistency(self):
        N = 2
        files = ["file1"]
        chunk_map = {"file1": ["chunk1"]}
        node_data = [
            {"chunk1": b""},
            {"chunk1": b""}
        ]
        self.assertTrue(are_chunks_consistent(N, files, chunk_map, node_data))

    def test_irrelevant_chunks_ignored(self):
        N = 2
        files = ["file1"]
        chunk_map = {"file1": ["chunk1"]}
        node_data = [
            {"chunk1": b"data", "unused_chunk": b"garbage"},
            {"chunk1": b"data", "unused_chunk": b"modified"}
        ]
        self.assertTrue(are_chunks_consistent(N, files, chunk_map, node_data))

    def test_some_nodes_missing_replica(self):
        N = 4
        files = ["fileA", "fileB"]
        chunk_map = {
            "fileA": ["chunk1", "chunk2"],
            "fileB": ["chunk3", "chunk4"]
        }
        node_data = [
            {"chunk1": b"X", "chunk2": b"Y", "chunk3": b"Z", "chunk4": b"W"},
            {"chunk1": b"X", "chunk2": None, "chunk3": b"Z", "chunk4": None},
            {"chunk1": None, "chunk2": b"Y", "chunk3": b"Z", "chunk4": b"W"},
            {"chunk1": b"X", "chunk2": b"Y", "chunk3": None, "chunk4": None}
        ]
        self.assertTrue(are_chunks_consistent(N, files, chunk_map, node_data))

    def test_multiple_files_and_edge_cases(self):
        N = 3
        files = ["file1", "file2"]
        chunk_map = {
            "file1": ["a", "b"],
            "file2": ["c", "d", "e"]
        }
        node_data = [
            {"a": b"one", "b": b"two", "c": None, "d": b"three", "e": b"four"},
            {"a": b"one", "b": b"different", "c": b"five", "d": b"three", "e": None},
            {"a": b"one", "b": b"two", "c": b"five", "d": None, "e": b"four"}
        ]
        self.assertFalse(are_chunks_consistent(N, files, chunk_map, node_data))

if __name__ == '__main__':
    unittest.main()