from typing import Dict, List, Set, Tuple
import heapq
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Job:
    job_id: str
    resource_requests: Dict[str, int]
    execution_time: int
    remaining_time: int
    weight: int
    preemption_cost: int
    start_time: int = -1
    
class Event:
    def __init__(self, time: int, job_id: str, event_type: str):
        self.time = time
        self.job_id = job_id
        self.event_type = event_type
        
    def to_dict(self) -> Dict:
        return {
            "time": self.time,
            "job_id": self.job_id,
            "event_type": self.event_type
        }

class ResourceManager:
    def __init__(self, resources: Dict[str, int]):
        self.total_resources = resources
        self.available_resources = resources.copy()
        
    def can_allocate(self, resource_requests: Dict[str, int]) -> bool:
        return all(
            self.available_resources[resource] >= request
            for resource, request in resource_requests.items()
        )
        
    def allocate(self, resource_requests: Dict[str, int]):
        for resource, request in resource_requests.items():
            self.available_resources[resource] -= request
            
    def release(self, resource_requests: Dict[str, int]):
        for resource, request in resource_requests.items():
            self.available_resources[resource] += request

class Scheduler:
    def __init__(self, resources: Dict[str, int], jobs: List[Dict], max_preemptions: int):
        self.resource_manager = ResourceManager(resources)
        self.jobs = {
            j["job_id"]: Job(
                j["job_id"],
                j["resource_requests"],
                j["execution_time"],
                j["execution_time"],
                j["weight"],
                j["preemption_cost"]
            ) for j in jobs
        }
        self.max_preemptions = max_preemptions
        self.current_time = 0
        self.events: List[Event] = []
        self.running_jobs: Set[str] = set()
        self.waiting_jobs: Set[str] = set(self.jobs.keys())
        self.preemption_count = 0
        
    def schedule(self) -> List[Dict]:
        while self.waiting_jobs or self.running_jobs:
            self._process_next_time_step()
            
        return [event.to_dict() for event in sorted(self.events, key=lambda e: (e.time, e.event_type))]
    
    def _process_next_time_step(self):
        # Try to start waiting jobs
        for job_id in list(self.waiting_jobs):
            job = self.jobs[job_id]
            if self.resource_manager.can_allocate(job.resource_requests):
                self._start_job(job)
                
        # Check if any running jobs complete
        completed_jobs = set()
        for job_id in self.running_jobs:
            job = self.jobs[job_id]
            job.remaining_time -= 1
            if job.remaining_time <= 0:
                completed_jobs.add(job_id)
                
        for job_id in completed_jobs:
            self._complete_job(self.jobs[job_id])
            
        # Consider preemption if beneficial
        if self.preemption_count < self.max_preemptions:
            self._try_preemption()
            
        self.current_time += 1
    
    def _start_job(self, job: Job):
        self.resource_manager.allocate(job.resource_requests)
        self.waiting_jobs.remove(job.job_id)
        self.running_jobs.add(job.job_id)
        job.start_time = self.current_time
        
        self.events.append(Event(self.current_time, job.job_id, "allocate"))
        self.events.append(Event(self.current_time, job.job_id, "start"))
    
    def _complete_job(self, job: Job):
        self.resource_manager.release(job.resource_requests)
        self.running_jobs.remove(job.job_id)
        self.events.append(Event(self.current_time, job.job_id, "finish"))
    
    def _try_preemption(self):
        if not self.waiting_jobs:
            return
            
        # Calculate potential benefit of preemption
        for running_job_id in self.running_jobs:
            running_job = self.jobs[running_job_id]
            for waiting_job_id in self.waiting_jobs:
                waiting_job = self.jobs[waiting_job_id]
                
                # Calculate if preemption would improve weighted completion time
                current_wct = (
                    running_job.weight * (self.current_time + running_job.remaining_time) +
                    waiting_job.weight * (self.current_time + running_job.remaining_time + waiting_job.execution_time)
                )
                
                preemption_wct = (
                    waiting_job.weight * (self.current_time + waiting_job.execution_time) +
                    running_job.weight * (
                        self.current_time + waiting_job.execution_time +
                        running_job.remaining_time + running_job.preemption_cost
                    )
                )
                
                if preemption_wct < current_wct and self.resource_manager.can_allocate(waiting_job.resource_requests):
                    self._preempt_job(running_job, waiting_job)
                    return
    
    def _preempt_job(self, running_job: Job, waiting_job: Job):
        # Preempt running job
        self.resource_manager.release(running_job.resource_requests)
        self.running_jobs.remove(running_job.job_id)
        self.waiting_jobs.add(running_job.job_id)
        running_job.remaining_time += running_job.preemption_cost
        self.events.append(Event(self.current_time, running_job.job_id, "preempt"))
        
        # Start waiting job
        self._start_job(waiting_job)
        self.preemption_count += 1

def allocate_resources(resources: Dict[str, int], jobs: List[Dict], max_preemptions: int) -> List[Dict]:
    scheduler = Scheduler(resources, jobs, max_preemptions)
    return scheduler.schedule()