from service_optimizer import optimize_communication

def main():
    # Example usage
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
        "D": []
    }
    L = {
        ("A", "B"): 10,
        ("A", "C"): 15,
        ("B", "D"): 20,
        ("C", "D"): 25
    }
    critical_pairs = {("A", "D")}
    C = {"B": 5, "C": 7, "D": 3}
    r = {"B": 6, "C": 8, "D": 4}
    B = 10
    R = 1
    p = 0.5

    cache_placement, replication_placement = optimize_communication(graph, L, critical_pairs, C, r, B, R, p)
    
    print("Optimized Communication Paths")
    print("-----------------------------")
    print(f"Cache Placement: {cache_placement}")
    print(f"Replication Placement: {replication_placement}")

if __name__ == "__main__":
    main()