from collections import deque

def can_commit_transaction(n, dependencies, initial_states):
    # Build the graph and reverse graph
    graph = [[] for _ in range(n)]
    reverse_graph = [[] for _ in range(n)]
    for a, b in dependencies:
        graph[a].append(b)  # a depends on b
        reverse_graph[b].append(a)  # b is depended on by a
    
    # Initialize abort status
    abort_status = [state == "ABORTED" for state in initial_states]
    queue = deque()
    
    # Initialize queue with initially aborted services
    for i in range(n):
        if abort_status[i]:
            queue.append(i)
    
    # Propagate abort signals
    while queue:
        service = queue.popleft()
        for dependent in reverse_graph[service]:
            if not abort_status[dependent]:
                abort_status[dependent] = True
                queue.append(dependent)
    
    # Check if any service is aborted
    return not any(abort_status)

def main():
    # Example usage
    n = 4
    dependencies = [(0, 1), (1, 2), (2, 0), (3, 1)]
    initial_states = ["READY", "READY", "ABORTED", "READY"]
    print(can_commit_transaction(n, dependencies, initial_states))  # Output: False

if __name__ == "__main__":
    main()