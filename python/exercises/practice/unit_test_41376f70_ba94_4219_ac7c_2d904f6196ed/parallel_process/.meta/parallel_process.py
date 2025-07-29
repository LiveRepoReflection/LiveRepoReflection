def distribute_data(N, K):
    """
    Distribute data across K worker nodes.
    
    Args:
        N (int): Total number of records to process
        K (int): Number of available worker nodes
        
    Returns:
        list: List of tuples (start_index, end_index, worker_id) representing data segments
    """
    distribution = []
    base_chunk_size = N // K
    remainder = N % K
    
    start = 0
    for worker_id in range(K):
        # Distribute remaining records evenly
        chunk_size = base_chunk_size + (1 if worker_id < remainder else 0)
        if chunk_size > 0:  # Only assign workers if they have work to do
            end = start + chunk_size - 1
            distribution.append((start, end, worker_id))
            start = end + 1
            
    return distribution


def process_data(data_segment):
    """
    Process a segment of data.
    
    Args:
        data_segment (tuple): (start_index, end_index) representing the data segment
        
    Returns:
        int: Sum of indices in the segment (simulated processing result)
    """
    start, end = data_segment
    # Simulate processing by summing the indices
    # For real implementation, this would perform the actual computation
    return sum(range(start, end + 1))


def recover_from_failure(failed_worker_id, N, K):
    """
    Recover from a worker failure by redistributing work.
    
    Args:
        failed_worker_id (int): ID of the failed worker
        N (int): Total number of records
        K (int): Total number of workers
        
    Returns:
        list: Updated distribution of data segments
    """
    # Step 1: Get the initial distribution
    initial_distribution = distribute_data(N, K)
    
    # Step 2: Extract segments assigned to the failed worker
    failed_segments = []
    active_segments = []
    
    for segment in initial_distribution:
        start, end, worker_id = segment
        if worker_id == failed_worker_id:
            failed_segments.append((start, end))
        else:
            active_segments.append(segment)
    
    # Step 3: Redistribute failed segments among remaining active workers
    active_worker_ids = [segment[2] for segment in active_segments]
    active_worker_ids = sorted(set(active_worker_ids))
    num_active_workers = len(active_worker_ids)
    
    # If no active workers remain, we can't recover
    if num_active_workers == 0:
        raise ValueError("No active workers available for recovery")
    
    # Redistribute each failed segment
    new_distribution = list(active_segments)
    
    for i, (start, end) in enumerate(failed_segments):
        segment_size = end - start + 1
        worker_id = active_worker_ids[i % num_active_workers]
        new_distribution.append((start, end, worker_id))
    
    return new_distribution


def aggregate_results(worker_results):
    """
    Aggregate results from all workers.
    
    Args:
        worker_results (list): List of worker results (sums)
        
    Returns:
        int: Sum of all worker results
    """
    return sum(worker_results)