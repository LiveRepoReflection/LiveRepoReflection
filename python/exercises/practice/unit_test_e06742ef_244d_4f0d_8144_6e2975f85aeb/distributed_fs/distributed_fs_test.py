import unittest
import threading
from distributed_fs import DistributedFileSystem

CHUNK_SIZE = 4096  # Assuming the constant used in the implementation

class TestDistributedFileSystem(unittest.TestCase):
    def setUp(self):
        # Initialize a distributed file system with 10 storage nodes and replication factor 3
        self.dfs = DistributedFileSystem(num_storage_nodes=10, replication_factor=3)

    def test_create_file_success(self):
        # Create a valid file
        result = self.dfs.create_file("/file1")
        self.assertTrue(result, "File should be created successfully.")

    def test_create_file_already_exists(self):
        # Create file and then attempt to create it again should fail
        self.dfs.create_file("/file2")
        result = self.dfs.create_file("/file2")
        self.assertFalse(result, "Creating an already existing file should return False.")

    def test_create_file_invalid_path(self):
        # File path without starting slash is invalid
        result = self.dfs.create_file("invalid_path")
        self.assertFalse(result, "Creating a file with invalid path should return False.")

    def test_write_and_read_file(self):
        # Write data to a file and read back the content
        file_path = "/file3"
        data = b"Hello, Distributed FS!"
        self.dfs.create_file(file_path)
        write_result = self.dfs.write_file(file_path, data)
        self.assertTrue(write_result, "Writing to an existing file should return True.")

        read_data = self.dfs.read_file(file_path)
        self.assertEqual(read_data, data, "Read data should match written data.")

    def test_write_file_not_existing(self):
        # Attempt to write to a non-existing file should return False
        file_path = "/nonexistent"
        data = b"Test Data"
        result = self.dfs.write_file(file_path, data)
        self.assertFalse(result, "Writing to a non-existent file should return False.")

    def test_read_file_not_existing(self):
        # Reading a non-existent file should return None
        read_data = self.dfs.read_file("/nonexistent_file")
        self.assertIsNone(read_data, "Reading a non-existent file should return None.")

    def test_delete_file_success(self):
        # Create and then delete a file successfully
        file_path = "/file4"
        self.dfs.create_file(file_path)
        delete_result = self.dfs.delete_file(file_path)
        self.assertTrue(delete_result, "Deleting an existing file should return True.")

        # After deletion, reading should return None
        read_data = self.dfs.read_file(file_path)
        self.assertIsNone(read_data, "After deletion, reading the file should return None.")

    def test_delete_file_not_found(self):
        # Attempting to delete a non-existent file should return False
        delete_result = self.dfs.delete_file("/nonexistent")
        self.assertFalse(delete_result, "Deleting a non-existent file should return False.")

    def test_overwrite_file(self):
        # Write initial data, then overwrite and check the content
        file_path = "/file5"
        initial_data = b"Initial Data"
        new_data = b"Overwritten Data"
        self.dfs.create_file(file_path)
        self.assertTrue(self.dfs.write_file(file_path, initial_data))
        self.assertEqual(self.dfs.read_file(file_path), initial_data)
        self.assertTrue(self.dfs.write_file(file_path, new_data))
        self.assertEqual(self.dfs.read_file(file_path), new_data)

    def test_chunking_handling(self):
        # Write a file that requires multiple chunks
        file_path = "/file6"
        data = b"A" * (CHUNK_SIZE * 2 + 100)  # Two full chunks + a partial one
        self.dfs.create_file(file_path)
        write_result = self.dfs.write_file(file_path, data)
        self.assertTrue(write_result, "Writing a multi-chunk file should return True.")
        read_data = self.dfs.read_file(file_path)
        self.assertEqual(read_data, data, "Data read should match the large written data.")

    def test_concurrent_writes(self):
        # Test concurrent writes to the same file
        file_path = "/file7"
        self.dfs.create_file(file_path)
        data1 = b"Thread1_Data"
        data2 = b"Thread2_Data"
        
        # Define write functions
        def write_data(data):
            self.dfs.write_file(file_path, data)
        
        t1 = threading.Thread(target=write_data, args=(data1,))
        t2 = threading.Thread(target=write_data, args=(data2,))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Read after concurrent writes; final content should be one of the two
        final_data = self.dfs.read_file(file_path)
        self.assertTrue(final_data in (data1, data2), 
                        "Final data should be written by one of the concurrent writers.")

    def test_replication_integrity(self):
        # Test that writing a file ensures that each chunk is replicated correctly.
        # We assume that the DFS implementation provides metadata about chunks and their placement.
        # For this test, after writing, we check that metadata for each chunk has K distinct storage nodes.
        file_path = "/file8"
        data = b"B" * (CHUNK_SIZE + 500)  # Data spans across two chunks
        self.dfs.create_file(file_path)
        write_result = self.dfs.write_file(file_path, data)
        self.assertTrue(write_result)
        
        # Assume the DFS implementation stores metadata in an attribute called 'metadata_store'
        # and that metadata_store[file_path]['chunks'] is a list of dictionaries with a key 'nodes'.
        metadata = self.dfs.metadata_store.get(file_path, {})
        self.assertIn('chunks', metadata, "Metadata should contain 'chunks' information.")

        for chunk in metadata.get('chunks', []):
            nodes = chunk.get('nodes', [])
            self.assertEqual(len(nodes), self.dfs.replication_factor,
                             "Each chunk should be replicated to the number of nodes equal to the replication factor.")
            # Check that all storage node IDs are distinct
            self.assertEqual(len(set(nodes)), len(nodes),
                             "Storage node IDs for a chunk should be distinct.")

if __name__ == '__main__':
    unittest.main()