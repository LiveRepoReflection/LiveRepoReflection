from time_router import find_optimal_route

def main():
    # Example usage
    graph = {
        1: [(2, 10, [(0, 100, 2.0)]), (3, 15, [(0, 50, 1.5)])],
        2: [(4, 20, [(0, 200, 1.5)])],
        3: [(4, 10, [(150, 250, 3.0)])],
        4: []
    }
    
    result = find_optimal_route(graph, 1, 4, 0)
    print(f"Minimum travel time: {result} minutes")

if __name__ == "__main__":
    main()