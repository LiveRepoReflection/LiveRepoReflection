import unittest
import time
import threading
import random
import string
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

# Import the necessary components from your implementation
from dist_file_sys import DistributedFileSystem, StorageNode, MetadataServer

class MockStorageNode(StorageNode):
    def __init__(self, node_id, fail_probability=0.0, delay_probability=0.0, max_delay=0.1):
        super().__init__(node_id)
        self.fail_probability = fail_probability
        self.delay_probability = delay_probability
        self.max_delay = max_delay
        
    def read_chunk(self, chunk_id):
        # Simulate random failures
        if random.random() < self.fail_probability:
            raise Exception(f"Storage node {self.node_id} failed to read chunk {chunk_id}")
        
        # Simulate random delays
        if random.random() < self.delay_probability:
            time.sleep(random.uniform(0, self.max_delay))
            
        return super().read_chunk(chunk_id)
        
    def write_chunk(self, chunk_id, data):
        # Simulate random failures
        if random.random() < self.fail_probability:
            raise Exception(f"Storage node {self.node_id} failed to write chunk {chunk_id}")
            
        # Simulate random delays
        if random.random() < self.delay_probability:
            time.sleep(random.uniform(0, self.max_delay))
            
        return super().write_chunk(chunk_id, data)

class TestDistributedFileSystem(unittest.TestCase):
    def setUp(self):
        # Initialize the system with default parameters
        self.num_nodes = 5
        self.replication_factor = 3
        self.chunk_size = 4  # Small chunk size for testing
        
        # Create storage nodes
        self.storage_nodes = [StorageNode(i) for i in range(self.num_nodes)]
        
        # Create metadata server
        self.metadata_server = MetadataServer()
        
        # Create the distributed file system
        self.dfs = DistributedFileSystem(
            self.storage_nodes,
            self.metadata_server,
            self.replication_factor,
            self.chunk_size
        )

    def generate_random_data(self, size):
        """Generate random data of specified size."""
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size)).encode()

    def test_basic_write_and_read(self):
        """Test basic write and read functionality."""
        file_path = "/test/file1.txt"
        content = b"This is a test file content."
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Read the file
        result = self.dfs.read(file_path)
        
        # Verify the content
        self.assertEqual(result.getvalue(), content)

    def test_large_file(self):
        """Test writing and reading a file larger than chunk size."""
        file_path = "/test/large_file.txt"
        content = self.generate_random_data(self.chunk_size * 10)  # 10 chunks
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Read the file
        result = self.dfs.read(file_path)
        
        # Verify the content
        self.assertEqual(result.getvalue(), content)

    def test_fault_tolerance(self):
        """Test fault tolerance with unresponsive nodes."""
        file_path = "/test/fault_tolerance.txt"
        content = self.generate_random_data(self.chunk_size * 5)  # 5 chunks
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Create a new DFS with some faulty nodes
        faulty_nodes = []
        for i in range(self.num_nodes):
            # Make some nodes fail with 100% probability
            if i < self.num_nodes - self.replication_factor:
                faulty_nodes.append(MockStorageNode(i, fail_probability=1.0))
            else:
                faulty_nodes.append(self.storage_nodes[i])
        
        faulty_dfs = DistributedFileSystem(
            faulty_nodes,
            self.metadata_server,
            self.replication_factor,
            self.chunk_size
        )
        
        # Read should still succeed because we have enough replicas
        result = faulty_dfs.read(file_path)
        self.assertEqual(result.getvalue(), content)

    def test_all_nodes_fail(self):
        """Test behavior when all nodes storing a chunk fail."""
        file_path = "/test/all_fail.txt"
        content = b"This file will be unreadable."
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Create a new DFS with all faulty nodes
        faulty_nodes = [MockStorageNode(i, fail_probability=1.0) for i in range(self.num_nodes)]
        
        faulty_dfs = DistributedFileSystem(
            faulty_nodes,
            self.metadata_server,
            self.replication_factor,
            self.chunk_size
        )
        
        # Read should fail because all replicas are unavailable
        with self.assertRaises(Exception):
            faulty_dfs.read(file_path)

    def test_concurrent_reads(self):
        """Test concurrent reads of the same file."""
        file_path = "/test/concurrent_reads.txt"
        content = self.generate_random_data(self.chunk_size * 3)
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Perform concurrent reads
        num_threads = 10
        results = []
        
        def read_file():
            result = self.dfs.read(file_path)
            results.append(result.getvalue())
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=read_file)
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify all reads were successful
        for result in results:
            self.assertEqual(result, content)

    def test_concurrent_writes(self):
        """Test concurrent writes to different files."""
        num_files = 5
        file_contents = {}
        
        # Generate file contents
        for i in range(num_files):
            file_path = f"/test/concurrent_write_{i}.txt"
            content = self.generate_random_data(self.chunk_size * 2)
            file_contents[file_path] = content
        
        # Perform concurrent writes
        def write_file(file_path, content):
            self.dfs.write(file_path, BytesIO(content))
        
        with ThreadPoolExecutor(max_workers=num_files) as executor:
            futures = []
            for file_path, content in file_contents.items():
                futures.append(executor.submit(write_file, file_path, content))
            
            # Wait for all writes to complete
            for future in futures:
                future.result()
        
        # Verify all files were written correctly
        for file_path, content in file_contents.items():
            result = self.dfs.read(file_path)
            self.assertEqual(result.getvalue(), content)

    def test_performance(self):
        """Test the performance of read and write operations."""
        file_path = "/test/performance.txt"
        content_size = self.chunk_size * 20  # 20 chunks
        content = self.generate_random_data(content_size)
        
        # Measure write time
        start_time = time.time()
        self.dfs.write(file_path, BytesIO(content))
        write_time = time.time() - start_time
        
        # Measure read time
        start_time = time.time()
        result = self.dfs.read(file_path)
        read_time = time.time() - start_time
        
        # Just make sure the operations complete in a reasonable time
        # Actual performance metrics will depend on the implementation and hardware
        print(f"Write time for {content_size} bytes: {write_time} seconds")
        print(f"Read time for {content_size} bytes: {read_time} seconds")
        
        # Verify the content
        self.assertEqual(result.getvalue(), content)

    def test_node_delays(self):
        """Test system behavior with delayed nodes."""
        file_path = "/test/delayed_nodes.txt"
        content = self.generate_random_data(self.chunk_size * 3)
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Create a new DFS with some delayed nodes
        delayed_nodes = []
        for i in range(self.num_nodes):
            # Make some nodes have delays
            if i < self.num_nodes // 2:
                delayed_nodes.append(MockStorageNode(i, delay_probability=1.0, max_delay=0.1))
            else:
                delayed_nodes.append(self.storage_nodes[i])
        
        delayed_dfs = DistributedFileSystem(
            delayed_nodes,
            self.metadata_server,
            self.replication_factor,
            self.chunk_size
        )
        
        # Read should still succeed but might take longer
        start_time = time.time()
        result = delayed_dfs.read(file_path)
        read_time = time.time() - start_time
        
        # Verify the content
        self.assertEqual(result.getvalue(), content)
        
        print(f"Read time with delayed nodes: {read_time} seconds")

    def test_round_robin_distribution(self):
        """Test that chunks are distributed in a round-robin fashion."""
        file_path = "/test/round_robin.txt"
        # Create a file with many chunks
        content = self.generate_random_data(self.chunk_size * self.num_nodes * 2)
        
        # Write the file
        self.dfs.write(file_path, BytesIO(content))
        
        # Get file metadata
        file_metadata = self.metadata_server.get_file_metadata(file_path)
        
        # Count chunks per node
        chunk_count_per_node = [0] * self.num_nodes
        for chunk_id, node_ids in file_metadata["chunk_locations"].items():
            for node_id in node_ids:
                chunk_count_per_node[node_id] += 1
        
        # Verify that chunks are evenly distributed (or close to it)
        # Calculate the expected number of chunks per node
        total_chunks = len(file_metadata["chunks"]) * self.replication_factor
        expected_chunks_per_node = total_chunks / self.num_nodes
        
        # Allow for some variation, but ensure distribution is reasonably even
        for count in chunk_count_per_node:
            self.assertLessEqual(abs(count - expected_chunks_per_node), 2)

    def test_nonexistent_file(self):
        """Test reading a nonexistent file."""
        with self.assertRaises(Exception):
            self.dfs.read("/nonexistent/file.txt")

    def test_empty_file(self):
        """Test writing and reading an empty file."""
        file_path = "/test/empty_file.txt"
        content = b""
        
        # Write the empty file
        self.dfs.write(file_path, BytesIO(content))
        
        # Read the file
        result = self.dfs.read(file_path)
        
        # Verify the content
        self.assertEqual(result.getvalue(), content)

if __name__ == "__main__":
    unittest.main()