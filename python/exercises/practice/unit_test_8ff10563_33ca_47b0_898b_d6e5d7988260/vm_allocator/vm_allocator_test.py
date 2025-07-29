import unittest
from datetime import datetime, timedelta

# Import the function to be tested
from vm_allocator import allocate_vms

class TestVMAllocator(unittest.TestCase):
    def test_empty_inputs(self):
        vm_instances = []
        requests = []
        result = allocate_vms(vm_instances, requests)
        self.assertEqual(result, {}, "Expected an empty allocation for empty inputs.")

    def test_no_available_vm(self):
        # When there are requests but no VMs available, allocation should be empty.
        vm_instances = []
        requests = [
            (1, 2, 4, 50, 5, 1000000),
            (2, 3, 6, 70, 8, 1000000)
        ]
        result = allocate_vms(vm_instances, requests)
        self.assertEqual(result, {}, "Expected empty allocation when no VMs are available.")

    def test_basic_allocation(self):
        # Basic test with three VMs and three requests.
        vm_instances = [
            (2, 4, 50, 10),   # VM 0
            (4, 8, 100, 20),  # VM 1
            (8, 16, 200, 35)  # VM 2
        ]
        # All requests have the same deadline.
        common_deadline = 1000000
        requests = [
            (1, 1, 2, 20, 5, common_deadline),   # Request 1: Low requirement
            (2, 3, 6, 70, 8, common_deadline),   # Request 2: Medium requirement
            (3, 6, 12, 150, 2, common_deadline)   # Request 3: High requirement, but low priority
        ]
        result = allocate_vms(vm_instances, requests)
        # The allocation must satisfy the resource requirements.
        # Since there are 3 requests and 3 VMs, a valid allocation is possible for at least two requests.
        self.assertTrue(isinstance(result, dict), "Result should be a dictionary.")
        for req in requests:
            req_id, req_cpu, req_ram, req_disk, priority, deadline = req
            if req_id in result:
                vm_idx = result[req_id]
                self.assertTrue(0 <= vm_idx < len(vm_instances), "Allocated VM index is out of range.")
                vm_cpu, vm_ram, vm_disk, cost = vm_instances[vm_idx]
                self.assertGreaterEqual(vm_cpu, req_cpu, f"VM {vm_idx} does not satisfy CPU requirement for request {req_id}.")
                self.assertGreaterEqual(vm_ram, req_ram, f"VM {vm_idx} does not satisfy RAM requirement for request {req_id}.")
                self.assertGreaterEqual(vm_disk, req_disk, f"VM {vm_idx} does not satisfy Disk requirement for request {req_id}.")

    def test_priority_deadline_allocation(self):
        # Test that when multiple requests compete for a single available VM,
        # the request with the higher priority and earlier deadline is favored.
        vm_instances = [
            (8, 16, 200, 35)  # Only one VM available
        ]
        now = int(datetime.now().timestamp())
        # Create three requests, all can be served by the single VM.
        requests = [
            (1, 4, 8, 100, 5, now + 600),  # Lower priority, deadline in 10 minutes
            (2, 4, 8, 100, 10, now + 1200), # Higher priority but later deadline
            (3, 4, 8, 100, 10, now + 300)   # Same high priority but earlier deadline
        ]
        result = allocate_vms(vm_instances, requests)
        # Only one request can be assigned because there is a single VM.
        self.assertEqual(len(result), 1, "Only one request should be allocated due to a single available VM.")
        # The chosen request should be Request 3 (highest priority and earliest deadline among the highest priority ones)
        allocated_req_id = next(iter(result))
        self.assertEqual(allocated_req_id, 3, "Request with highest priority and earliest deadline should be selected.")

    def test_over_allocation_penalty_effect(self):
        # Test scenario where over-allocation penalty affects the cost decision.
        # Two VMs can satisfy the request, but one VM provides excess resources.
        vm_instances = [
            (4, 8, 100, 20),  # VM 0: closer to requirement
            (8, 16, 200, 35)  # VM 1: has surplus resources leading to potential penalty
        ]
        common_deadline = 1000000
        # Request exactly matches lower-tier VM requirements.
        requests = [
            (1, 4, 8, 100, 7, common_deadline)
        ]
        result = allocate_vms(vm_instances, requests)
        # Expect the allocation to choose the better matching VM (VM 0) to minimize cost including waste.
        self.assertIn(1, result, "Request should be allocated a VM.")
        self.assertEqual(result[1], 0, "The allocation should favor the VM with closer resource match (VM 0).")

    def test_multiple_allocations(self):
        # Test scenario with multiple VMs and requests to ensure maximum utilization.
        vm_instances = [
            (2, 4, 50, 10),   # VM 0
            (4, 8, 100, 20),  # VM 1
            (8, 16, 200, 35), # VM 2
            (16, 32, 400, 60) # VM 3
        ]
        common_deadline = 1000000
        requests = [
            (1, 2, 4, 50, 5, common_deadline),   # Should match VM 0 ideally
            (2, 3, 6, 70, 8, common_deadline),     # Should match VM 1 ideally
            (3, 8, 16, 200, 6, common_deadline),   # Should match VM 2 ideally
            (4, 10, 20, 150, 9, common_deadline),  # May be allocated to VM 3
            (5, 16, 32, 400, 3, common_deadline)   # High requirement; only VM 3 qualifies if not taken
        ]
        result = allocate_vms(vm_instances, requests)
        # The allocation should maximize the number of satisfied requests
        self.assertTrue(len(result) >= 3, "At least three requests should be allocated in this scenario.")
        # Verify each allocated VM has sufficient resources for its corresponding request.
        for req in requests:
            req_id, req_cpu, req_ram, req_disk, priority, deadline = req
            if req_id in result:
                vm_idx = result[req_id]
                self.assertTrue(0 <= vm_idx < len(vm_instances), f"Allocated VM index {vm_idx} out of range.")
                vm_cpu, vm_ram, vm_disk, cost = vm_instances[vm_idx]
                self.assertGreaterEqual(vm_cpu, req_cpu, f"VM {vm_idx} does not meet CPU requirement for request {req_id}.")
                self.assertGreaterEqual(vm_ram, req_ram, f"VM {vm_idx} does not meet RAM requirement for request {req_id}.")
                self.assertGreaterEqual(vm_disk, req_disk, f"VM {vm_idx} does not meet Disk requirement for request {req_id}.")

    def test_scalability(self):
        # Test scalability by generating a large number of VMs and requests.
        num_vms = 1000
        num_requests = 1000
        vm_instances = []
        for i in range(num_vms):
            # Generate VMs with increasing resources and cost.
            vm_instances.append((2 + i % 5, 4 + i % 10, 50 + i % 20, 10 + i % 10))
        
        now = int(datetime.now().timestamp())
        requests = []
        for j in range(num_requests):
            # Generate requests with random requirements within a range.
            req_cpu = 2 + j % 3
            req_ram = 4 + j % 5
            req_disk = 50 + j % 10
            priority = (j % 10) + 1
            deadline = now + ((j % 5) * 60)  # deadlines vary within next few minutes
            requests.append((j, req_cpu, req_ram, req_disk, priority, deadline))
        
        result = allocate_vms(vm_instances, requests)
        # Ensure that the result is a dictionary and does not allocate more than available VMs.
        self.assertIsInstance(result, dict, "Result should be a dictionary.")
        self.assertLessEqual(len(result), num_requests, "Allocated requests cannot exceed total number of requests.")
        for req in requests:
            req_id, req_cpu, req_ram, req_disk, priority, deadline = req
            if req_id in result:
                vm_idx = result[req_id]
                vm_cpu, vm_ram, vm_disk, cost = vm_instances[vm_idx]
                self.assertGreaterEqual(vm_cpu, req_cpu, f"VM {vm_idx} does not meet CPU requirement for request {req_id}.")
                self.assertGreaterEqual(vm_ram, req_ram, f"VM {vm_idx} does not meet RAM requirement for request {req_id}.")
                self.assertGreaterEqual(vm_disk, req_disk, f"VM {vm_idx} does not meet Disk requirement for request {req_id}.")

if __name__ == '__main__':
    unittest.main()