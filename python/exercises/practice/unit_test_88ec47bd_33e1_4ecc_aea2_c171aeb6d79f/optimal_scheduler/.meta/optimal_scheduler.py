import heapq

def find_min_max_lateness(n, tasks):
    # Sort tasks by deadline
    sorted_tasks = sorted(tasks, key=lambda x: x[1])
    
    # Initialize a min-heap with finish times for each worker
    worker_heap = [0] * n
    heapq.heapify(worker_heap)
    
    max_lateness = 0
    
    for processing_time, deadline in sorted_tasks:
        # Get the worker that will be free earliest
        current_time = heapq.heappop(worker_heap)
        new_finish = current_time + processing_time
        # Calculate lateness for this task
        lateness = max(0, new_finish - deadline)
        if lateness > max_lateness:
            max_lateness = lateness
        # Assign the task and update the worker's finish time
        heapq.heappush(worker_heap, new_finish)
    
    return max_lateness

if __name__ == '__main__':
    # Sample run for quick validation
    n = 2
    tasks = [(2, 5), (1, 3), (3, 8), (2, 4)]
    print(find_min_max_lateness(n, tasks))