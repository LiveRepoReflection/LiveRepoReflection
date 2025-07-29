import unittest
from cloud_alloc import allocate_resources

class TestCloudAlloc(unittest.TestCase):
    def validate_allocation(self, allocation, cpu_demand, memory_demand, network_demand, num_replicas, 
                            cpu_capacity, memory_capacity, network_capacity, vm_types_count):
        # Verify that allocation is a dictionary with valid keys.
        self.assertIsInstance(allocation, dict)
        total_required_replicas = sum(num_replicas)
        allocated_replicas = 0
        
        # Count occurrences of each microservice replica
        microservice_counts = {}
        
        for vm_type, assignments in allocation.items():
            # Check VM type key is valid.
            self.assertIsInstance(vm_type, int)
            self.assertGreaterEqual(vm_type, 0)
            self.assertLess(vm_type, vm_types_count)
            self.assertIsInstance(assignments, list)
            
            # For each VM instance allocation, sum the resource usage.
            total_cpu = 0
            total_memory = 0
            total_network = 0
            for ms in assignments:
                self.assertIsInstance(ms, int)
                # ms index must be valid (based on length of cpu_demand etc.)
                self.assertGreaterEqual(ms, 0)
                self.assertLess(ms, len(cpu_demand))
                total_cpu += cpu_demand[ms]
                total_memory += memory_demand[ms]
                total_network += network_demand[ms]
                # Count the replica for this microservice
                microservice_counts[ms] = microservice_counts.get(ms, 0) + 1
                
            # Check that the total allocation does not exceed the capacity of the VM type.
            self.assertLessEqual(total_cpu, cpu_capacity[vm_type], 
                                 f"CPU demand exceeded for VM type {vm_type}")
            self.assertLessEqual(total_memory, memory_capacity[vm_type],
                                 f"Memory demand exceeded for VM type {vm_type}")
            self.assertLessEqual(total_network, network_capacity[vm_type],
                                 f"Network demand exceeded for VM type {vm_type}")
            
            allocated_replicas += len(assignments)
        
        # Check that all replicas are assigned exactly
        self.assertEqual(allocated_replicas, total_required_replicas, 
                         "Total number of allocated replicas does not match required replicas.")
        for i, req in enumerate(num_replicas):
            self.assertEqual(microservice_counts.get(i, 0), req,
                             f"Microservice {i} replica count mismatch. Expected {req}, got {microservice_counts.get(i, 0)}")

    def test_single_microservice_single_vm(self):
        # One microservice, one replica, one VM type.
        cpu_demand = [2]
        memory_demand = [4]
        network_demand = [10]
        priority = [5]
        num_replicas = [1]
        
        cost_per_hour = [1.0]
        cpu_capacity = [2]
        memory_capacity = [4]
        network_capacity = [10]
        
        allocation = allocate_resources(cpu_demand, memory_demand, network_demand, 
                                        priority, num_replicas, 
                                        cost_per_hour, cpu_capacity, memory_capacity, network_capacity)
        
        self.validate_allocation(allocation, cpu_demand, memory_demand, network_demand, num_replicas, 
                                 cpu_capacity, memory_capacity, network_capacity, len(cost_per_hour))

    def test_example_scenario(self):
        # Example as provided in the problem description.
        cpu_demand = [2, 4]
        memory_demand = [4, 8]
        network_demand = [100, 200]
        priority = [10, 5]
        num_replicas = [2, 1]
        
        cost_per_hour = [1.0, 2.0]
        cpu_capacity = [8, 16]
        memory_capacity = [16, 32]
        network_capacity = [400, 800]
        
        allocation = allocate_resources(cpu_demand, memory_demand, network_demand, 
                                        priority, num_replicas, 
                                        cost_per_hour, cpu_capacity, memory_capacity, network_capacity)
        
        self.validate_allocation(allocation, cpu_demand, memory_demand, network_demand, num_replicas, 
                                 cpu_capacity, memory_capacity, network_capacity, len(cost_per_hour))
    
    def test_multiple_services_multiple_vm_types(self):
        # More complex scenario with multiple microservices and VM types.
        cpu_demand = [1, 3, 2, 4]
        memory_demand = [2, 6, 4, 8]
        network_demand = [50, 150, 100, 200]
        priority = [8, 10, 7, 5]
        num_replicas = [3, 2, 2, 1]
        
        cost_per_hour = [1.0, 1.5, 2.0]
        cpu_capacity = [5, 10, 8]
        memory_capacity = [10, 20, 16]
        network_capacity = [250, 500, 400]
        
        allocation = allocate_resources(cpu_demand, memory_demand, network_demand, 
                                        priority, num_replicas, 
                                        cost_per_hour, cpu_capacity, memory_capacity, network_capacity)
        
        self.validate_allocation(allocation, cpu_demand, memory_demand, network_demand, num_replicas, 
                                 cpu_capacity, memory_capacity, network_capacity, len(cost_per_hour))
    
    def test_tight_capacity(self):
        # Scenario where capacities are tight and order of allocation is crucial.
        cpu_demand = [2, 2, 3]
        memory_demand = [4, 4, 6]
        network_demand = [100, 90, 120]
        priority = [9, 8, 7]
        num_replicas = [1, 1, 1]
        
        cost_per_hour = [1.0, 2.0]
        cpu_capacity = [5, 6]
        memory_capacity = [9, 10]
        network_capacity = [190, 220]
        
        allocation = allocate_resources(cpu_demand, memory_demand, network_demand, 
                                        priority, num_replicas, 
                                        cost_per_hour, cpu_capacity, memory_capacity, network_capacity)
        
        self.validate_allocation(allocation, cpu_demand, memory_demand, network_demand, num_replicas, 
                                 cpu_capacity, memory_capacity, network_capacity, len(cost_per_hour))

if __name__ == '__main__':
    unittest.main()