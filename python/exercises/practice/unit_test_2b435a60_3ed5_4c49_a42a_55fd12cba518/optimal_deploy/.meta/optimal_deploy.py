import math

def find_optimal_deployment(graph, T, C, costs):
    n = len(costs)
    # Precompute all pairs shortest paths using Floyd Warshall
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for i in graph:
        for j in graph[i]:
            # Since the graph is undirected, update both directions.
            dist[i][j] = graph[i][j]
            if i not in graph.get(j, {}):
                # Ensure symmetry if not provided
                if j < n and i < n:
                    dist[j][i] = graph[i][j]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Check feasibility: every node must at least cover itself.
    for i in range(n):
        if dist[i][i] > T:
            return set(), -1

    # Data structures to keep track of assignment.
    # assignment[j] = (server, distance) indicating node j is served by 'server' with given distance.
    assignment = {}
    # open_servers: mapping from server id to list of nodes assigned (server always serves itself with 0 distance)
    open_servers = {}

    # Helper: for each already open server with available capacity, try to assign uncovered nodes.
    def assign_using_open_servers():
        progress = True
        while progress:
            progress = False
            for j in range(n):
                if j in assignment:
                    continue
                best_server = None
                best_distance = INF
                for s in open_servers:
                    # If server s has available capacity
                    if len(open_servers[s]) < C and dist[s][j] <= T:
                        if dist[s][j] < best_distance:
                            best_distance = dist[s][j]
                            best_server = s
                if best_server is not None:
                    assignment[j] = (best_server, best_distance)
                    open_servers[best_server].append(j)
                    progress = True

    # Initially, try to assign nodes using open servers (none are open yet)
    assign_using_open_servers()

    # While there exist uncovered nodes:
    while len(assignment) < n:
        # For each candidate server that is not open, compute potential coverage among uncovered nodes.
        candidate_metrics = []
        for i in range(n):
            # Skip if already opened as a server
            if i in open_servers:
                continue
            # Candidate i always covers itself (distance = 0), so candidate coverage is not empty.
            coverage = []
            for j in range(n):
                if j not in assignment and dist[i][j] <= T:
                    coverage.append((j, dist[i][j]))
            # If none uncovered can be served by candidate i, skip.
            if not coverage:
                continue
            # Sort coverage by distance
            coverage.sort(key=lambda x: x[1])
            # Due to capacity, candidate can only serve up to C nodes.
            num_assigned = min(len(coverage), C)
            selected = coverage[:num_assigned]
            total_assignment_cost = sum(d for (_, d) in selected)
            # Metric: (fixed cost + assignment cost) per node covered.
            metric = (costs[i] + total_assignment_cost) / num_assigned
            candidate_metrics.append((metric, i, selected))
        if not candidate_metrics:
            return set(), -1  # No candidate can cover any uncovered node; infeasible.
        # Choose candidate with minimal metric.
        candidate_metrics.sort(key=lambda x: x[0])
        _, chosen_server, chosen_assignment = candidate_metrics[0]
        # Open this server.
        open_servers[chosen_server] = []
        # Immediately assign the server itself if not already assigned.
        if chosen_server not in assignment:
            assignment[chosen_server] = (chosen_server, 0)
            open_servers[chosen_server].append(chosen_server)
        # For selected nodes that are still uncovered, assign them.
        for j, d in chosen_assignment:
            if j not in assignment:
                assignment[j] = (chosen_server, d)
                open_servers[chosen_server].append(j)
                # If capacity reached, break.
                if len(open_servers[chosen_server]) >= C:
                    break
        # After opening a new server, try to assign more nodes using open servers.
        assign_using_open_servers()

    # Compute total latency: sum of distances for each node assignment.
    total_latency = sum(dist for (_, dist) in assignment.values())
    # The set of servers is the keys of open_servers.
    deployed_servers = set(open_servers.keys())
    return deployed_servers, total_latency