class Machine:
    """
    Represents a machine in the cluster with specific resource capacities.
    
    Attributes:
        id (int): Unique identifier for the machine
        total_cpu (int): Total CPU cores available
        total_memory (int): Total memory in GB available
        total_gpu (int): Total GPU units available
        used_cpu (int): Currently used CPU cores
        used_memory (int): Currently used memory in GB
        used_gpu (int): Currently used GPU units
    """
    def __init__(self, id, total_cpu, total_memory, total_gpu):
        self.id = id
        self.total_cpu = total_cpu
        self.total_memory = total_memory
        self.total_gpu = total_gpu
        self.used_cpu = 0
        self.used_memory = 0
        self.used_gpu = 0
    
    @property
    def available_cpu(self):
        """Returns the available CPU cores."""
        return self.total_cpu - self.used_cpu
    
    @property
    def available_memory(self):
        """Returns the available memory in GB."""
        return self.total_memory - self.used_memory
    
    @property
    def available_gpu(self):
        """Returns the available GPU units."""
        return self.total_gpu - self.used_gpu
    
    def can_allocate(self, job):
        """
        Checks if the job can be allocated to this machine.
        
        Args:
            job (Job): Job to check allocation possibility for
            
        Returns:
            bool: True if job can be allocated, False otherwise
        """
        return (
            self.available_cpu >= job.required_cpu and
            self.available_memory >= job.required_memory and
            self.available_gpu >= job.required_gpu
        )
    
    def allocate(self, job):
        """
        Allocates resources for a job on this machine.
        
        Args:
            job (Job): Job to allocate resources for
            
        Returns:
            bool: True if allocation was successful, False otherwise
        """
        if not self.can_allocate(job):
            return False
        
        self.used_cpu += job.required_cpu
        self.used_memory += job.required_memory
        self.used_gpu += job.required_gpu
        return True
    
    def deallocate(self, job):
        """
        Deallocates resources used by a job on this machine.
        
        Args:
            job (Job): Job to deallocate resources for
        """
        self.used_cpu = max(0, self.used_cpu - job.required_cpu)
        self.used_memory = max(0, self.used_memory - job.required_memory)
        self.used_gpu = max(0, self.used_gpu - job.required_gpu)
    
    def resource_utilization_ratio(self):
        """
        Calculates the overall resource utilization ratio of this machine.
        
        Returns:
            float: Resource utilization ratio between 0.0 and 1.0
        """
        if self.total_cpu == 0 and self.total_memory == 0 and self.total_gpu == 0:
            return 0.0
            
        cpu_ratio = self.used_cpu / self.total_cpu if self.total_cpu > 0 else 0
        memory_ratio = self.used_memory / self.total_memory if self.total_memory > 0 else 0
        gpu_ratio = self.used_gpu / self.total_gpu if self.total_gpu > 0 else 0
        
        # Calculate weighted average based on resource importance
        # Here we consider all resources equally important
        total_weights = 3
        if self.total_cpu == 0:
            total_weights -= 1
        if self.total_memory == 0:
            total_weights -= 1
        if self.total_gpu == 0:
            total_weights -= 1
            
        if total_weights == 0:
            return 0.0
            
        return (cpu_ratio + memory_ratio + gpu_ratio) / total_weights
        
    def __str__(self):
        return f"Machine {self.id}: CPU {self.used_cpu}/{self.total_cpu}, " \
               f"Memory {self.used_memory}/{self.total_memory} GB, " \
               f"GPU {self.used_gpu}/{self.total_gpu}"


class Job:
    """
    Represents a job to be executed on a machine.
    
    Attributes:
        id (int): Unique identifier for the job
        required_cpu (int): CPU cores required
        required_memory (int): Memory in GB required
        required_gpu (int): GPU units required
    """
    def __init__(self, id, required_cpu, required_memory, required_gpu):
        self.id = id
        self.required_cpu = required_cpu
        self.required_memory = required_memory
        self.required_gpu = required_gpu
    
    def __str__(self):
        return f"Job {self.id}: Requires CPU {self.required_cpu}, " \
               f"Memory {self.required_memory} GB, GPU {self.required_gpu}"


def allocate_job(machines, job):
    """
    Allocates a job to one of the available machines using a hybrid approach 
    that combines best-fit and resource-balanced strategies.
    
    The strategy attempts to:
    1. Find machines that can accommodate the job
    2. Score each machine based on resource utilization and fit
    3. Select the machine with the best score (minimizing fragmentation
       while balancing load across resources)
    
    Args:
        machines (list): List of Machine objects
        job (Job): Job to be allocated
        
    Returns:
        int or None: ID of the machine to which job is allocated, or None if no suitable machine
    """
    # Edge cases
    if not machines:
        return None
    
    # If job requires zero resources, allocate to the least utilized machine
    if job.required_cpu == 0 and job.required_memory == 0 and job.required_gpu == 0:
        return machines[0].id if machines else None
    
    # Find all machines that can accommodate the job
    candidates = [machine for machine in machines if machine.can_allocate(job)]
    
    if not candidates:
        return None
    
    # Define a score function for each machine based on resource utilization and fit
    def score_machine(machine):
        # Calculate how close the resources will be to full after allocation
        # Lower score is better (less wastage)
        cpu_fit = (machine.used_cpu + job.required_cpu) / machine.total_cpu if machine.total_cpu > 0 else 0
        memory_fit = (machine.used_memory + job.required_memory) / machine.total_memory if machine.total_memory > 0 else 0
        gpu_fit = (machine.used_gpu + job.required_gpu) / machine.total_gpu if machine.total_gpu > 0 else 0
        
        # Variance in resource utilization (lower is better, indicating balanced usage)
        values = [x for x in [cpu_fit, memory_fit, gpu_fit] if x > 0]
        
        if not values:
            return float('inf')  # Should never happen with valid candidates
            
        average = sum(values) / len(values)
        variance = sum((x - average) ** 2 for x in values) / len(values)
        
        # Our score is a combination of:
        # 1. Average resource utilization (best-fit strategy)
        # 2. Resource utilization variance (balance between resource types)
        # Lower score is better
        return 0.7 * average + 0.3 * variance
    
    # Select the best machine based on our scoring function
    best_machine = min(candidates, key=score_machine)
    
    # Allocate the job to the best machine
    if best_machine.allocate(job):
        return best_machine.id
    
    return None


def deallocate_job(machines, machine_id, job):
    """
    Deallocates a job from a specific machine.
    
    Args:
        machines (list): List of Machine objects
        machine_id (int): ID of the machine from which to deallocate
        job (Job): Job to be deallocated
    """
    # Find the machine with the given ID
    machine = next((m for m in machines if m.id == machine_id), None)
    
    if machine:
        machine.deallocate(job)