import unittest
from resource_allocator import allocate_resources

class ResourceAllocatorTest(unittest.TestCase):
    def test_basic_allocation(self):
        resources = {"CPU": 20, "Memory": 40}
        jobs = [
            {
                "job_id": "job1",
                "resource_requests": {"CPU": 10, "Memory": 20},
                "execution_time": 5,
                "weight": 2,
                "preemption_cost": 1
            },
            {
                "job_id": "job2",
                "resource_requests": {"CPU": 5, "Memory": 10},
                "execution_time": 10,
                "weight": 1,
                "preemption_cost": 0
            }
        ]
        max_preemptions = 0
        
        schedule = allocate_resources(resources, jobs, max_preemptions)
        
        # Verify schedule structure
        self.assertIsInstance(schedule, list)
        for event in schedule:
            self.assertIsInstance(event, dict)
            self.assertIn('time', event)
            self.assertIn('job_id', event)
            self.assertIn('event_type', event)
            self.assertIn(event['event_type'], ['allocate', 'start', 'preempt', 'resume', 'finish'])

    def test_resource_constraints(self):
        resources = {"CPU": 10, "Memory": 20}
        jobs = [
            {
                "job_id": "job1",
                "resource_requests": {"CPU": 8, "Memory": 16},
                "execution_time": 5,
                "weight": 1,
                "preemption_cost": 1
            },
            {
                "job_id": "job2",
                "resource_requests": {"CPU": 4, "Memory": 8},
                "execution_time": 3,
                "weight": 1,
                "preemption_cost": 1
            }
        ]
        max_preemptions = 0
        
        schedule = allocate_resources(resources, jobs, max_preemptions)
        
        # Track resource usage over time
        time_points = sorted(set(event['time'] for event in schedule))
        for t in time_points:
            cpu_usage = 0
            memory_usage = 0
            running_jobs = set()
            
            # Process all events up to this time
            for event in schedule:
                if event['time'] > t:
                    break
                    
                if event['event_type'] == 'allocate':
                    job = next(j for j in jobs if j['job_id'] == event['job_id'])
                    cpu_usage += job['resource_requests']['CPU']
                    memory_usage += job['resource_requests']['Memory']
                    running_jobs.add(event['job_id'])
                elif event['event_type'] == 'finish':
                    job = next(j for j in jobs if j['job_id'] == event['job_id'])
                    cpu_usage -= job['resource_requests']['CPU']
                    memory_usage -= job['resource_requests']['Memory']
                    running_jobs.remove(event['job_id'])
                    
            # Verify resource constraints
            self.assertLessEqual(cpu_usage, resources['CPU'])
            self.assertLessEqual(memory_usage, resources['Memory'])

    def test_preemption_limit(self):
        resources = {"CPU": 10}
        jobs = [
            {
                "job_id": "job1",
                "resource_requests": {"CPU": 5},
                "execution_time": 5,
                "weight": 1,
                "preemption_cost": 1
            },
            {
                "job_id": "job2",
                "resource_requests": {"CPU": 5},
                "execution_time": 5,
                "weight": 2,
                "preemption_cost": 1
            }
        ]
        max_preemptions = 1
        
        schedule = allocate_resources(resources, jobs, max_preemptions)
        
        # Count preemptions
        preemption_count = sum(1 for event in schedule if event['event_type'] == 'preempt')
        self.assertLessEqual(preemption_count, max_preemptions)

    def test_completion_times(self):
        resources = {"CPU": 10}
        jobs = [
            {
                "job_id": "job1",
                "resource_requests": {"CPU": 5},
                "execution_time": 3,
                "weight": 1,
                "preemption_cost": 1
            }
        ]
        max_preemptions = 0
        
        schedule = allocate_resources(resources, jobs, max_preemptions)
        
        # Verify job completion
        job_starts = {}
        job_finishes = {}
        
        for event in schedule:
            if event['event_type'] == 'start':
                job_starts[event['job_id']] = event['time']
            elif event['event_type'] == 'finish':
                job_finishes[event['job_id']] = event['time']
        
        for job in jobs:
            job_id = job['job_id']
            self.assertIn(job_id, job_starts)
            self.assertIn(job_id, job_finishes)
            expected_finish = job_starts[job_id] + job['execution_time']
            self.assertLessEqual(job_finishes[job_id], expected_finish)

    def test_complex_scenario(self):
        resources = {"CPU": 20, "Memory": 40, "GPU": 2}
        jobs = [
            {
                "job_id": "job1",
                "resource_requests": {"CPU": 10, "Memory": 20, "GPU": 1},
                "execution_time": 5,
                "weight": 3,
                "preemption_cost": 1
            },
            {
                "job_id": "job2",
                "resource_requests": {"CPU": 5, "Memory": 10, "GPU": 1},
                "execution_time": 8,
                "weight": 2,
                "preemption_cost": 1
            },
            {
                "job_id": "job3",
                "resource_requests": {"CPU": 8, "Memory": 15, "GPU": 1},
                "execution_time": 3,
                "weight": 1,
                "preemption_cost": 2
            }
        ]
        max_preemptions = 2
        
        schedule = allocate_resources(resources, jobs, max_preemptions)
        
        # Verify all jobs are completed
        completed_jobs = set(event['job_id'] for event in schedule if event['event_type'] == 'finish')
        self.assertEqual(completed_jobs, set(job['job_id'] for job in jobs))

    def test_edge_cases(self):
        # Test empty job list
        resources = {"CPU": 10}
        jobs = []
        max_preemptions = 0
        schedule = allocate_resources(resources, jobs, max_preemptions)
        self.assertEqual(schedule, [])
        
        # Test single resource, single job
        jobs = [
            {
                "job_id": "job1",
                "resource_requests": {"CPU": 1},
                "execution_time": 1,
                "weight": 1,
                "preemption_cost": 0
            }
        ]
        schedule = allocate_resources(resources, jobs, max_preemptions)
        self.assertTrue(any(event['event_type'] == 'finish' for event in schedule))

if __name__ == '__main__':
    unittest.main()