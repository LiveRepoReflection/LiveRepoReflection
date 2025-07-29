def allocate_nodes(node_resources, job_request):
    M = len(job_request)
    # If job_request is all zeros, then no nodes are needed.
    if all(x == 0 for x in job_request):
        return 0

    # Helper to add two resource vectors and clip them at job_request.
    def add_resources(current, node):
        return tuple(min(current[i] + node[i], job_request[i]) for i in range(M))
    
    # Starting DP: state -> minimum number of nodes used.
    # State is represented as a tuple of resources accumulated (clipped to job_request)
    start = tuple(0 for _ in range(M))
    dp = {start: 0}
    goal = tuple(job_request)

    for node in node_resources:
        # We make a copy of current states to iterate over.
        current_states = list(dp.items())
        for state, count in current_states:
            new_state = add_resources(state, node)
            new_count = count + 1
            # If reaching goal with current node, update if will use fewer nodes.
            if new_state not in dp or dp[new_state] > new_count:
                dp[new_state] = new_count

    # After processing all nodes, check if goal state was reached.
    return dp.get(goal, -1)

if __name__ == "__main__":
    # Basic manual testing if required.
    nodes = [[5, 3], [2, 4], [3, 1]]
    request = [7, 5]
    print(allocate_nodes(nodes, request))