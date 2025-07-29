import unittest
from storage_allocator import optimize_storage_allocation


class StorageAllocatorTest(unittest.TestCase):
    def test_simple_allocation(self):
        devices = [
            ("device1", 100, {"A", "B", "C"}),
            ("device2", 50, {"B", "D"}),
            ("device3", 75, {"A", "C"}),
        ]

        chunks = [
            ("chunk1", 30, {"A", "C"}),
            ("chunk2", 20, {"B"}),
            ("chunk3", 60, {"A"}),
            ("chunk4", 40, {"B", "D"}),
        ]

        allocation = optimize_storage_allocation(devices, chunks)
        
        # Check if all chunks are allocated
        all_allocated_chunks = []
        for chunks_list in allocation.values():
            all_allocated_chunks.extend(chunks_list)
        
        self.assertEqual(len(all_allocated_chunks), 4)
        
        # Check if each chunk is allocated exactly once
        self.assertEqual(len(set(all_allocated_chunks)), 4)
        
        # Check if each allocated device exists in the input
        device_ids = {device[0] for device in devices}
        for device_id in allocation.keys():
            if device_id != "unallocated":
                self.assertIn(device_id, device_ids)

    def test_capacity_constraints(self):
        devices = [
            ("device1", 50, {"A", "B"}),
        ]

        chunks = [
            ("chunk1", 30, {"A"}),
            ("chunk2", 30, {"B"}),
            ("chunk3", 20, {"A"}),
        ]

        allocation = optimize_storage_allocation(devices, chunks)
        
        # Verify the device isn't overloaded
        for device_id, chunk_ids in allocation.items():
            if device_id == "unallocated":
                continue
                
            device_capacity = next(device[1] for device in devices if device[0] == device_id)
            total_allocated = sum(next(chunk[1] for chunk in chunks if chunk[0] == chunk_id) for chunk_id in chunk_ids)
            self.assertLessEqual(total_allocated, device_capacity)
        
        # At least one chunk should be unallocated due to capacity constraints
        self.assertTrue("unallocated" in allocation and len(allocation["unallocated"]) > 0)

    def test_affinity_requirements(self):
        devices = [
            ("device1", 100, {"A", "B"}),
            ("device2", 100, {"C", "D"}),
        ]

        chunks = [
            ("chunk1", 30, {"A"}),
            ("chunk2", 40, {"C"}),
            ("chunk3", 20, {"E"}),
        ]

        allocation = optimize_storage_allocation(devices, chunks)
        
        # Verify that chunks are allocated to devices with matching capabilities
        for device_id, chunk_ids in allocation.items():
            if device_id == "unallocated":
                # Check that unallocated chunks don't have matching devices
                for chunk_id in chunk_ids:
                    chunk_req = next(chunk[2] for chunk in chunks if chunk[0] == chunk_id)
                    for device in devices:
                        if chunk_req.issubset(device[2]) and sum(next(c[1] for c in chunks if c[0] == cid) for cid in allocation.get(device[0], [])) + next(c[1] for c in chunks if c[0] == chunk_id) <= device[1]:
                            self.fail(f"Chunk {chunk_id} could have been allocated to device {device[0]}")
                continue
                
            device_capabilities = next(device[2] for device in devices if device[0] == device_id)
            for chunk_id in chunk_ids:
                chunk_requirements = next(chunk[2] for chunk in chunks if chunk[0] == chunk_id)
                self.assertTrue(chunk_requirements.issubset(device_capabilities))

    def test_empty_inputs(self):
        # Test with no devices
        allocation = optimize_storage_allocation([], [("chunk1", 10, {"A"})])
        self.assertEqual(allocation, {"unallocated": ["chunk1"]})
        
        # Test with no chunks
        allocation = optimize_storage_allocation([("device1", 100, {"A"})], [])
        self.assertEqual(allocation, {})

    def test_complex_allocation(self):
        devices = [
            ("device1", 100, {"A", "B", "C"}),
            ("device2", 200, {"B", "D", "E"}),
            ("device3", 150, {"A", "C", "F"}),
            ("device4", 80, {"D", "E", "F"}),
            ("device5", 120, {"A", "B", "D", "F"}),
        ]

        chunks = [
            ("chunk1", 40, {"A", "B"}),
            ("chunk2", 30, {"B", "D"}),
            ("chunk3", 70, {"A", "C"}),
            ("chunk4", 50, {"D", "E"}),
            ("chunk5", 90, {"A", "F"}),
            ("chunk6", 60, {"B", "E"}),
            ("chunk7", 100, {"A", "B", "C"}),
            ("chunk8", 20, {"D", "F"}),
            ("chunk9", 80, {"A", "B", "D"}),
            ("chunk10", 10, {"C", "F"}),
        ]

        allocation = optimize_storage_allocation(devices, chunks)
        
        # Check all chunks are allocated or in unallocated list
        all_chunks_accounted_for = []
        for chunks_list in allocation.values():
            all_chunks_accounted_for.extend(chunks_list)
        
        self.assertEqual(sorted(all_chunks_accounted_for), sorted([chunk[0] for chunk in chunks]))
        
        # Check capacity constraints for each device
        for device_id, chunk_ids in allocation.items():
            if device_id == "unallocated":
                continue
                
            device_capacity = next(device[1] for device in devices if device[0] == device_id)
            total_allocated = sum(next(chunk[1] for chunk in chunks if chunk[0] == chunk_id) for chunk_id in chunk_ids)
            self.assertLessEqual(total_allocated, device_capacity)
            
        # Check affinity requirements
        for device_id, chunk_ids in allocation.items():
            if device_id == "unallocated":
                continue
                
            device_capabilities = next(device[2] for device in devices if device[0] == device_id)
            for chunk_id in chunk_ids:
                chunk_requirements = next(chunk[2] for chunk in chunks if chunk[0] == chunk_id)
                self.assertTrue(chunk_requirements.issubset(device_capabilities))

    def test_optimization_goal(self):
        # Test that the solution uses the minimum number of devices
        devices = [
            ("device1", 100, {"A", "B"}),
            ("device2", 100, {"A", "B"}),
            ("device3", 100, {"A", "B"}),
        ]

        chunks = [
            ("chunk1", 60, {"A"}),
            ("chunk2", 70, {"B"}),
            ("chunk3", 40, {"A", "B"}),
        ]

        allocation = optimize_storage_allocation(devices, chunks)
        
        # The optimal solution should use exactly 2 devices (not 3)
        device_count = sum(1 for device_id in allocation if device_id != "unallocated")
        self.assertEqual(device_count, 2)
        
        # Check that all chunks are allocated
        self.assertTrue("unallocated" not in allocation or len(allocation["unallocated"]) == 0)

    def test_large_allocation(self):
        # Generate a larger test case
        import random
        random.seed(42)  # For reproducibility
        
        capabilities = ["A", "B", "C", "D", "E", "F", "G", "H"]
        
        devices = []
        for i in range(50):
            capacity = random.randint(100, 1000)
            device_capabilities = set(random.sample(capabilities, random.randint(2, 5)))
            devices.append((f"device{i}", capacity, device_capabilities))
            
        chunks = []
        for i in range(200):
            size = random.randint(10, 200)
            required_capabilities = set(random.sample(capabilities, random.randint(1, 3)))
            chunks.append((f"chunk{i}", size, required_capabilities))
            
        allocation = optimize_storage_allocation(devices, chunks)
        
        # Check that chunks are allocated to devices with matching capabilities
        for device_id, chunk_ids in allocation.items():
            if device_id == "unallocated":
                continue
                
            device_capabilities = next(device[2] for device in devices if device[0] == device_id)
            for chunk_id in chunk_ids:
                chunk_requirements = next(chunk[2] for chunk in chunks if chunk[0] == chunk_id)
                self.assertTrue(chunk_requirements.issubset(device_capabilities))
                
        # Check capacity constraints
        for device_id, chunk_ids in allocation.items():
            if device_id == "unallocated":
                continue
                
            device_capacity = next(device[1] for device in devices if device[0] == device_id)
            total_allocated = sum(next(chunk[1] for chunk in chunks if chunk[0] == chunk_id) for chunk_id in chunk_ids)
            self.assertLessEqual(total_allocated, device_capacity)
            
        # Make sure all chunks are accounted for
        all_allocated = []
        for chunks_list in allocation.values():
            all_allocated.extend(chunks_list)
            
        self.assertEqual(len(set(all_allocated)), len(chunks))
        
    def test_invalid_inputs(self):
        # Test with invalid device format
        with self.assertRaises(Exception):
            optimize_storage_allocation([("device1", "100", {"A"})], [("chunk1", 10, {"A"})])
            
        # Test with invalid chunk format
        with self.assertRaises(Exception):
            optimize_storage_allocation([("device1", 100, {"A"})], [("chunk1", "10", {"A"})])
            
        # Test with invalid capabilities format
        with self.assertRaises(Exception):
            optimize_storage_allocation([("device1", 100, "A")], [("chunk1", 10, {"A"})])


if __name__ == "__main__":
    unittest.main()