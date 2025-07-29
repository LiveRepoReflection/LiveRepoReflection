import unittest
import hashlib
import uuid
from typing import Dict, List, Set
import copy
import threading
import random
from data_integrity import detect_and_correct_corruption, NodeData

class TestDataIntegrity(unittest.TestCase):
    def generate_test_data(self, num_nodes, num_blocks, corruption_rate=0):
        """Generate test data for specified number of nodes and blocks"""
        node_data = {}
        block_uuids = [str(uuid.uuid4()) for _ in range(num_blocks)]
        
        # First create uncorrupted data for all nodes
        for node_id in range(num_nodes):
            data_blocks = {}
            checksums = {}
            
            for block_uuid in block_uuids:
                # Generate random data for each block
                data = bytes([random.randint(0, 255) for _ in range(random.randint(10, 100))])
                data_blocks[block_uuid] = data
                checksums[block_uuid] = hashlib.sha256(data).hexdigest()
            
            node_data[node_id] = NodeData(data_blocks, checksums)
        
        # Now introduce corruption if requested
        if corruption_rate > 0:
            for node_id in range(num_nodes):
                for block_uuid in block_uuids:
                    if random.random() < corruption_rate:
                        # Corrupt data (change data but not checksum)
                        corrupted_data = bytearray(node_data[node_id].data_blocks[block_uuid])
                        pos = random.randint(0, len(corrupted_data) - 1)
                        corrupted_data[pos] = (corrupted_data[pos] + 1) % 256
                        node_data[node_id].data_blocks[block_uuid] = bytes(corrupted_data)
        
        return node_data, block_uuids

    def test_no_corruption(self):
        """Test that system works when there's no corruption"""
        node_data, block_uuids = self.generate_test_data(num_nodes=3, num_blocks=5)
        suspected_nodes = [1]  # Suspect node 1 even though it's not corrupted
        
        result, unrecoverable = detect_and_correct_corruption(3, node_data, suspected_nodes)
        
        # Should have no unrecoverable blocks
        self.assertEqual(len(unrecoverable), 0)
        
        # Data should be unchanged
        for node_id in range(3):
            for block_uuid in block_uuids:
                self.assertEqual(
                    node_data[node_id].data_blocks[block_uuid],
                    result[node_id].data_blocks[block_uuid]
                )

    def test_single_node_corruption(self):
        """Test corruption in a single node that can be recovered from other nodes"""
        node_data, block_uuids = self.generate_test_data(num_nodes=3, num_blocks=5)
        
        # Manually corrupt one block in node 1
        corrupted_block = block_uuids[0]
        original_data = node_data[1].data_blocks[corrupted_block]
        corrupted_data = bytearray(original_data)
        corrupted_data[0] = (corrupted_data[0] + 1) % 256
        node_data[1].data_blocks[corrupted_block] = bytes(corrupted_data)
        
        suspected_nodes = [1]
        
        result, unrecoverable = detect_and_correct_corruption(3, node_data, suspected_nodes)
        
        # Should have no unrecoverable blocks
        self.assertEqual(len(unrecoverable), 0)
        
        # Corrupted block should be fixed
        self.assertEqual(
            result[1].data_blocks[corrupted_block],
            node_data[0].data_blocks[corrupted_block]  # Should match node 0's data
        )
        
        # Checksum should match data
        self.assertEqual(
            result[1].checksums[corrupted_block],
            hashlib.sha256(result[1].data_blocks[corrupted_block]).hexdigest()
        )

    def test_multiple_node_corruption(self):
        """Test corruption across multiple nodes"""
        node_data, block_uuids = self.generate_test_data(num_nodes=5, num_blocks=10)
        
        # Corrupt the same block in nodes 1, 3, and 4
        corrupted_block = block_uuids[0]
        for node_id in [1, 3, 4]:
            original_data = node_data[node_id].data_blocks[corrupted_block]
            corrupted_data = bytearray(original_data)
            corrupted_data[0] = (corrupted_data[0] + node_id) % 256  # Different corruption per node
            node_data[node_id].data_blocks[corrupted_block] = bytes(corrupted_data)
        
        suspected_nodes = [1, 3, 4]
        
        result, unrecoverable = detect_and_correct_corruption(5, node_data, suspected_nodes)
        
        # Should have no unrecoverable blocks
        self.assertEqual(len(unrecoverable), 0)
        
        # All corrupted blocks should be fixed and match node 0's data
        for node_id in suspected_nodes:
            self.assertEqual(
                result[node_id].data_blocks[corrupted_block],
                node_data[0].data_blocks[corrupted_block]
            )
            
            self.assertEqual(
                result[node_id].checksums[corrupted_block],
                hashlib.sha256(result[node_id].data_blocks[corrupted_block]).hexdigest()
            )

    def test_unrecoverable_corruption(self):
        """Test case where all versions of a block are corrupted"""
        node_data, block_uuids = self.generate_test_data(num_nodes=3, num_blocks=5)
        
        # Corrupt the same block in all nodes but with different corruption
        corrupted_block = block_uuids[0]
        for node_id in range(3):
            original_data = node_data[node_id].data_blocks[corrupted_block]
            corrupted_data = bytearray(original_data)
            corrupted_data[0] = (corrupted_data[0] + node_id + 1) % 256
            node_data[node_id].data_blocks[corrupted_block] = bytes(corrupted_data)
        
        suspected_nodes = [0, 1, 2]  # All nodes suspected
        
        result, unrecoverable = detect_and_correct_corruption(3, node_data, suspected_nodes)
        
        # The corrupted block should be unrecoverable
        self.assertEqual(unrecoverable, [corrupted_block])
        
        # Corrupted blocks should remain unchanged
        for node_id in range(3):
            self.assertEqual(
                result[node_id].data_blocks[corrupted_block],
                node_data[node_id].data_blocks[corrupted_block]
            )

    def test_partial_corruption(self):
        """Test partial corruption where some blocks are corrupted on all nodes"""
        node_data, block_uuids = self.generate_test_data(num_nodes=4, num_blocks=6)
        
        # Corrupt block 0 on node 1 only (recoverable)
        corrupted_block1 = block_uuids[0]
        original_data = node_data[1].data_blocks[corrupted_block1]
        corrupted_data = bytearray(original_data)
        corrupted_data[0] = (corrupted_data[0] + 1) % 256
        node_data[1].data_blocks[corrupted_block1] = bytes(corrupted_data)
        
        # Corrupt block 1 on all nodes (unrecoverable)
        corrupted_block2 = block_uuids[1]
        for node_id in range(4):
            original_data = node_data[node_id].data_blocks[corrupted_block2]
            corrupted_data = bytearray(original_data)
            corrupted_data[0] = (corrupted_data[0] + node_id + 1) % 256
            node_data[node_id].data_blocks[corrupted_block2] = bytes(corrupted_data)
        
        suspected_nodes = [0, 1, 2, 3]
        
        result, unrecoverable = detect_and_correct_corruption(4, node_data, suspected_nodes)
        
        # Block 1 should be unrecoverable
        self.assertEqual(unrecoverable, [corrupted_block2])
        
        # Block 0 should be fixed on node 1
        self.assertEqual(
            result[1].data_blocks[corrupted_block1],
            node_data[0].data_blocks[corrupted_block1]  # Should match node 0's data
        )

    def test_large_scale(self):
        """Test with a larger number of nodes and blocks"""
        node_data, block_uuids = self.generate_test_data(num_nodes=10, num_blocks=20, corruption_rate=0.1)
        suspected_nodes = list(range(10))  # Suspect all nodes
        
        result, unrecoverable = detect_and_correct_corruption(10, node_data, suspected_nodes)
        
        # Just verify the function runs without errors for large datasets
        self.assertIsNotNone(result)
        self.assertIsInstance(unrecoverable, list)

    def test_thread_safety(self):
        """Test that the function is thread-safe"""
        node_data, block_uuids = self.generate_test_data(num_nodes=5, num_blocks=10, corruption_rate=0.2)
        suspected_nodes = list(range(5))
        
        # Create deep copies for each thread to use
        node_data_copies = [copy.deepcopy(node_data) for _ in range(3)]
        results = [None, None, None]
        unrecoverables = [None, None, None]
        
        def run_detection(index):
            results[index], unrecoverables[index] = detect_and_correct_corruption(
                5, node_data_copies[index], suspected_nodes
            )
        
        # Run detection in multiple threads
        threads = [threading.Thread(target=run_detection, args=(i,)) for i in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All threads should produce the same result
        for i in range(1, 3):
            for node_id in range(5):
                for block_uuid in block_uuids:
                    self.assertEqual(
                        results[0][node_id].data_blocks[block_uuid],
                        results[i][node_id].data_blocks[block_uuid]
                    )
        
        # Unrecoverable sets should be identical
        self.assertEqual(set(unrecoverables[0]), set(unrecoverables[1]))
        self.assertEqual(set(unrecoverables[0]), set(unrecoverables[2]))

    def test_mixed_corruption_patterns(self):
        """Test various corruption patterns in the same system"""
        node_data, block_uuids = self.generate_test_data(num_nodes=6, num_blocks=8)
        
        # Block 0: Corrupt on node 2 only (recoverable)
        corrupted_block1 = block_uuids[0]
        original_data = node_data[2].data_blocks[corrupted_block1]
        corrupted_data = bytearray(original_data)
        corrupted_data[0] = (corrupted_data[0] + 1) % 256
        node_data[2].data_blocks[corrupted_block1] = bytes(corrupted_data)
        
        # Block 1: Corrupt on nodes 0, 1, 2 but uncorrupted on 3, 4, 5 (recoverable)
        corrupted_block2 = block_uuids[1]
        for node_id in range(3):
            original_data = node_data[node_id].data_blocks[corrupted_block2]
            corrupted_data = bytearray(original_data)
            corrupted_data[0] = (corrupted_data[0] + 1) % 256
            node_data[node_id].data_blocks[corrupted_block2] = bytes(corrupted_data)
        
        # Block 2: Corrupt on all nodes (unrecoverable)
        corrupted_block3 = block_uuids[2]
        for node_id in range(6):
            original_data = node_data[node_id].data_blocks[corrupted_block3]
            corrupted_data = bytearray(original_data)
            corrupted_data[0] = (corrupted_data[0] + node_id + 1) % 256
            node_data[node_id].data_blocks[corrupted_block3] = bytes(corrupted_data)
        
        suspected_nodes = [0, 1, 2, 3, 4, 5]
        
        result, unrecoverable = detect_and_correct_corruption(6, node_data, suspected_nodes)
        
        # Only Block 2 should be unrecoverable
        self.assertEqual(unrecoverable, [corrupted_block3])
        
        # Block 0 should be fixed on node 2
        self.assertEqual(
            result[2].data_blocks[corrupted_block1],
            node_data[0].data_blocks[corrupted_block1]  # Should match node 0's data
        )
        
        # Block 1 should be fixed on nodes 0, 1, 2
        for node_id in range(3):
            self.assertEqual(
                result[node_id].data_blocks[corrupted_block2],
                node_data[3].data_blocks[corrupted_block2]  # Should match uncorrupted node 3's data
            )

    def test_partial_suspicion(self):
        """Test when only some corrupted nodes are suspected"""
        node_data, block_uuids = self.generate_test_data(num_nodes=4, num_blocks=5)
        
        # Corrupt block 0 on nodes 1 and 3
        corrupted_block = block_uuids[0]
        for node_id in [1, 3]:
            original_data = node_data[node_id].data_blocks[corrupted_block]
            corrupted_data = bytearray(original_data)
            corrupted_data[0] = (corrupted_data[0] + 1) % 256
            node_data[node_id].data_blocks[corrupted_block] = bytes(corrupted_data)
        
        # Only suspect node 1
        suspected_nodes = [1]
        
        result, unrecoverable = detect_and_correct_corruption(4, node_data, suspected_nodes)
        
        # Should have no unrecoverable blocks
        self.assertEqual(len(unrecoverable), 0)
        
        # Node 1 should be fixed
        self.assertEqual(
            result[1].data_blocks[corrupted_block],
            node_data[0].data_blocks[corrupted_block]
        )
        
        # Node 3 should remain corrupted as it wasn't suspected
        self.assertEqual(
            result[3].data_blocks[corrupted_block],
            node_data[3].data_blocks[corrupted_block]
        )

if __name__ == "__main__":
    unittest.main()