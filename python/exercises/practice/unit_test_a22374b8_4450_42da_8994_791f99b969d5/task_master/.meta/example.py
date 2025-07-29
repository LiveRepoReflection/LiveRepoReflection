from task_master import schedule_tasks
from visualization import visualize_schedule, visualize_dependency_graph

def main():
    """
    Example usage of the task scheduler with visualization
    """
    # Basic example
    print("Basic Example")
    tasks = [
        (1, 1, [], 5),  # Task 1, priority 1, no dependencies, execution time 5 seconds
        (2, 2, [1], 3), # Task 2, priority 2, depends on Task 1, execution time 3 seconds
        (3, 1, [], 4),  # Task 3, priority 1, no dependencies, execution time 4 seconds
        (4, 3, [2, 3], 2) # Task 4, priority 3, depends on Tasks 2 and 3, execution time 2 seconds
    ]
    num_workers = 2
    
    schedule = schedule_tasks(tasks, num_workers)
    
    print("Schedule:")
    for event in schedule:
        timestamp, worker_id, event_type, task_id = event
        print(f"Time {timestamp}: Worker {worker_id} - {event_type} Task {task_id}")
    
    # Try to visualize if matplotlib is available
    try:
        visualize_schedule(schedule, tasks, num_workers)
        visualize_dependency_graph(tasks)
    except ImportError:
        print("Matplotlib is required for visualization.")
    
    # Complex example with more tasks and dependencies
    print("\nComplex Example")
    complex_tasks = [
        (1, 1, [], 2),
        (2, 1, [1], 2),
        (3, 1, [1], 3),
        (4, 2, [2, 3], 2),
        (5, 2, [3], 1),
        (6, 3, [4, 5], 2),
        (7, 2, [], 3),
        (8, 1, [7], 2),
        (9, 3, [6, 8], 4)
    ]
    num_workers = 3
    
    schedule = schedule_tasks(complex_tasks, num_workers, failure_probability=0.1)
    
    print("Schedule:")
    for event in schedule:
        timestamp, worker_id, event_type, task_id = event
        print(f"Time {timestamp}: Worker {worker_id} - {event_type} Task {task_id}")
    
    # Try to visualize if matplotlib is available
    try:
        visualize_schedule(schedule, complex_tasks, num_workers)
        visualize_dependency_graph(complex_tasks)
    except ImportError:
        print("Matplotlib is required for visualization.")

if __name__ == "__main__":
    main()