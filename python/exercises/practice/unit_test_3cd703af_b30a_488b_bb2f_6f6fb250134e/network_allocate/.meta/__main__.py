from .network_allocate import find_optimal_path

def main():
    """
    Example usage of the find_optimal_path function.
    """
    # Example from the problem statement
    capacities = {(0, 1): 10.0, (1, 2): 5.0, (0, 2): 12.0}
    costs = {(0, 1): 1.0, (1, 2): 2.0, (0, 2): 3.0}
    allocations = {(0, 1): 3.0, (1, 2): 1.0, (0, 2): 5.0}
    source = 0
    destination = 2
    bandwidth = 4.0
    
    result = find_optimal_path(capacities, costs, allocations, source, destination, bandwidth)
    
    if result:
        path, total_cost = result
        print(f"Optimal path: {path}")
        print(f"Total cost: {total_cost}")
    else:
        print("No feasible path found.")

if __name__ == "__main__":
    main()