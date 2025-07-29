import itertools
from collections import defaultdict

def net_deploy(N, K, adjacency_matrix, service_dependencies, dependency_latency_threshold,
              node_resources, service_requirements, replication_factor,
              node_failures_tolerated, service_communication):
    # Precompute shortest paths between all nodes
    shortest_paths = [[float('inf')] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if adjacency_matrix[i][j] != -1:
                shortest_paths[i][j] = adjacency_matrix[i][j]
    
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if shortest_paths[i][j] > shortest_paths[i][k] + shortest_paths[k][j]:
                    shortest_paths[i][j] = shortest_paths[i][k] + shortest_paths[k][j]

    # Generate all possible node combinations for each service
    service_nodes = []
    for service in range(K):
        possible_nodes = []
        for node in range(N):
            # Check if node has enough resources for this service
            if (node_resources[node][0] >= service_requirements[service][0] and
                node_resources[node][1] >= service_requirements[service][1] and
                node_resources[node][2] >= service_requirements[service][2]):
                possible_nodes.append(node)
        service_nodes.append(possible_nodes)

    # Check if any service has no possible nodes
    if any(len(nodes) == 0 for nodes in service_nodes):
        return {}

    # Generate all possible deployment combinations
    best_deployment = {}
    min_latency = float('inf')

    # We'll use a backtracking approach with pruning to find a valid deployment
    def backtrack(current_deployment, service, used_resources):
        nonlocal best_deployment, min_latency

        if service == K:
            # Check if the deployment meets all constraints
            if is_valid_deployment(current_deployment):
                # Calculate total weighted latency
                latency = calculate_latency(current_deployment)
                if latency < min_latency:
                    min_latency = latency
                    best_deployment = {k: v.copy() for k, v in current_deployment.items()}
            return

        # Try all possible node combinations for this service
        for nodes in itertools.combinations(service_nodes[service], replication_factor):
            # Check if these nodes would exceed resource constraints
            temp_resources = [list(res) for res in used_resources]
            valid = True
            for node in nodes:
                temp_resources[node][0] -= service_requirements[service][0]
                temp_resources[node][1] -= service_requirements[service][1]
                temp_resources[node][2] -= service_requirements[service][2]
                if temp_resources[node][0] < 0 or temp_resources[node][1] < 0 or temp_resources[node][2] < 0:
                    valid = False
                    break
            
            if not valid:
                continue

            current_deployment[service] = list(nodes)
            backtrack(current_deployment, service + 1, temp_resources)
            del current_deployment[service]

    def is_valid_deployment(deployment):
        # Check replication factor
        if any(len(nodes) != replication_factor for nodes in deployment.values()):
            return False

        # Check fault tolerance
        for service in range(K):
            for node in deployment[service]:
                # Check if removing node_failures_tolerated nodes still leaves enough replicas
                remaining_nodes = [n for n in deployment[service] if n != node]
                if len(remaining_nodes) < replication_factor - node_failures_tolerated:
                    return False

        # Check service dependencies
        for s2 in service_dependencies:
            for s1 in service_dependencies[s2]:
                for node2 in deployment[s2]:
                    # Check if at least one instance of s1 is within threshold
                    if not any(shortest_paths[node2][node1] <= dependency_latency_threshold 
                              for node1 in deployment[s1]):
                        return False
        return True

    def calculate_latency(deployment):
        total_latency = 0
        for s1 in range(K):
            for s2 in range(K):
                if service_communication[s1][s2] > 0:
                    # Calculate average latency between all instances of s1 and s2
                    sum_latency = 0
                    count = 0
                    for node1 in deployment[s1]:
                        for node2 in deployment[s2]:
                            sum_latency += shortest_paths[node1][node2]
                            count += 1
                    if count > 0:
                        avg_latency = sum_latency / count
                        total_latency += avg_latency * service_communication[s1][s2]
        return total_latency

    # Start backtracking
    initial_resources = [list(res) for res in node_resources]
    backtrack({}, 0, initial_resources)

    return best_deployment