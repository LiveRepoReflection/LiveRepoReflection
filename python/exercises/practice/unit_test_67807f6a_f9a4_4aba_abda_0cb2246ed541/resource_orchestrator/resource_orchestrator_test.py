import unittest
from resource_orchestrator import Machine, Job, allocate_job, deallocate_job

class ResourceOrchestratorTest(unittest.TestCase):
    def setUp(self):
        # Create a list of machines with different resource capacities
        self.machines = [
            Machine(1, 8, 16, 2),  # 8 CPU cores, 16 GB RAM, 2 GPUs
            Machine(2, 4, 8, 1),   # 4 CPU cores, 8 GB RAM, 1 GPU
            Machine(3, 16, 32, 4), # 16 CPU cores, 32 GB RAM, 4 GPUs
            Machine(4, 2, 4, 0)    # 2 CPU cores, 4 GB RAM, 0 GPUs
        ]
        
    def test_machine_initialization(self):
        machine = Machine(1, 8, 16, 2)
        self.assertEqual(machine.id, 1)
        self.assertEqual(machine.total_cpu, 8)
        self.assertEqual(machine.total_memory, 16)
        self.assertEqual(machine.total_gpu, 2)
        self.assertEqual(machine.used_cpu, 0)
        self.assertEqual(machine.used_memory, 0)
        self.assertEqual(machine.used_gpu, 0)
        
    def test_job_initialization(self):
        job = Job(1, 2, 4, 1)
        self.assertEqual(job.id, 1)
        self.assertEqual(job.required_cpu, 2)
        self.assertEqual(job.required_memory, 4)
        self.assertEqual(job.required_gpu, 1)
        
    def test_allocate_job_successful(self):
        job = Job(1, 2, 4, 1)
        machine_id = allocate_job(self.machines, job)
        self.assertIsNotNone(machine_id)
        
        # Find the machine where the job was allocated
        allocated_machine = next((m for m in self.machines if m.id == machine_id), None)
        self.assertIsNotNone(allocated_machine)
        
        # Check if resources were allocated correctly
        self.assertEqual(allocated_machine.used_cpu, 2)
        self.assertEqual(allocated_machine.used_memory, 4)
        self.assertEqual(allocated_machine.used_gpu, 1)
        
    def test_allocate_job_unsuccessful(self):
        # Create a job that requires more resources than any machine has
        job = Job(2, 20, 40, 5)
        machine_id = allocate_job(self.machines, job)
        self.assertIsNone(machine_id)
        
    def test_deallocate_job(self):
        job = Job(3, 4, 8, 2)
        machine_id = allocate_job(self.machines, job)
        self.assertIsNotNone(machine_id)
        
        # Find the machine where the job was allocated
        allocated_machine = next((m for m in self.machines if m.id == machine_id), None)
        self.assertIsNotNone(allocated_machine)
        
        # Record the used resources before deallocation
        used_cpu_before = allocated_machine.used_cpu
        used_memory_before = allocated_machine.used_memory
        used_gpu_before = allocated_machine.used_gpu
        
        # Deallocate the job
        deallocate_job(self.machines, machine_id, job)
        
        # Check if resources were deallocated correctly
        self.assertEqual(allocated_machine.used_cpu, used_cpu_before - job.required_cpu)
        self.assertEqual(allocated_machine.used_memory, used_memory_before - job.required_memory)
        self.assertEqual(allocated_machine.used_gpu, used_gpu_before - job.required_gpu)
        
    def test_allocate_multiple_jobs(self):
        jobs = [
            Job(4, 2, 4, 1),
            Job(5, 3, 6, 1),
            Job(6, 1, 2, 0)
        ]
        
        machine_ids = []
        for job in jobs:
            machine_id = allocate_job(self.machines, job)
            self.assertIsNotNone(machine_id)
            machine_ids.append(machine_id)
        
        # Check all jobs were allocated
        self.assertEqual(len(machine_ids), len(jobs))
        
    def test_allocate_job_edge_cases(self):
        # Job with zero resource requirements
        job_zero = Job(7, 0, 0, 0)
        machine_id = allocate_job(self.machines, job_zero)
        self.assertIsNotNone(machine_id)
        
        # Empty machine list
        empty_machines = []
        job = Job(8, 1, 2, 0)
        machine_id = allocate_job(empty_machines, job)
        self.assertIsNone(machine_id)
        
    def test_resource_constraints(self):
        # Fill up a machine's resources
        machine = self.machines[1]  # Machine with 4 CPU, 8 GB RAM, 1 GPU
        job1 = Job(9, 3, 6, 1)  # Uses most resources but leaves some CPU and memory
        
        machine_id = allocate_job([machine], job1)
        self.assertEqual(machine_id, machine.id)
        
        # Try to allocate another job that requires more resources than available
        job2 = Job(10, 2, 3, 0)  # Requires more CPU than what's left
        machine_id = allocate_job([machine], job2)
        self.assertIsNone(machine_id)
        
        # Try a job that fits within remaining resources
        job3 = Job(11, 1, 2, 0)  # Fits within remaining resources
        machine_id = allocate_job([machine], job3)
        self.assertEqual(machine_id, machine.id)
        
    def test_allocation_strategy(self):
        # Fill each machine with different amounts of resources to test the allocation strategy
        jobs = [
            Job(12, 2, 4, 1),  # Should go to machine 1
            Job(13, 1, 2, 1),  # Should go to machine 2
            Job(14, 8, 16, 2)  # Should go to machine 3
        ]
        
        # Allocate the jobs
        for job in jobs:
            allocate_job(self.machines, job)
        
        # Now allocate a small job and see which machine is chosen
        # The specific machine chosen will depend on the allocation strategy
        test_job = Job(15, 1, 2, 0)
        machine_id = allocate_job(self.machines, test_job)
        self.assertIsNotNone(machine_id)
        
        # We just verify that a machine was found, the specific ID depends on the strategy

if __name__ == '__main__':
    unittest.main()