import heapq

def find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate):
    # If demand is 0, no cost is incurred
    if demand == 0:
        return 0

    # Check if source and destination nodes have enough capacity
    if nodes[source][0] < demand or nodes[destination][0] < demand:
        return -1

    # Calculate the required minimum survival probability
    required_survival = 1 - max_packet_loss_rate

    # Build an undirected graph: for each edge (u, v, latency, loss), add both u->v and v->u.
    graph = {i: [] for i in range(len(nodes))}
    for u, v, latency, loss in edges:
        graph[u].append((v, latency, loss))
        graph[v].append((u, latency, loss))
        
    # Use a variant of Dijkstra with state [cost, node, latency, survival_probability]
    # Start with the source, initial cost is processing cost at source.
    initial_cost = demand * nodes[source][1]
    start_state = (initial_cost, source, 0, 1.0)
    heap = [start_state]

    # dp will store for each node, a list of tuples (latency, survival, cost) we have seen.
    dp = {i: [] for i in range(len(nodes))}
    dp[source].append((0, 1.0, initial_cost))

    while heap:
        current_cost, node, current_latency, current_survival = heapq.heappop(heap)
        
        # If we reached destination and satisfy constraints, return the current cost.
        if node == destination:
            if current_latency <= max_latency and current_survival >= required_survival:
                return current_cost
        
        # Explore neighbors
        for neighbor, edge_latency, edge_loss in graph[node]:
            # Check node capacity at neighbor
            if nodes[neighbor][0] < demand:
                continue

            new_latency = current_latency + edge_latency
            if new_latency > max_latency:
                continue

            new_survival = current_survival * (1 - edge_loss)
            # Since survival only decreases with additional hops, if it is already below requirement, skip.
            if new_survival < required_survival:
                continue

            new_cost = current_cost + demand * nodes[neighbor][1]
            new_state = (new_latency, new_survival, new_cost)
            
            # Prune suboptimal states using dp[neighbor].
            dominated = False
            indices_to_remove = []
            for idx, (lat, surv, cost_val) in enumerate(dp[neighbor]):
                # If existing state is no worse in all criteria, then the new state is dominated.
                if lat <= new_latency and surv >= new_survival and cost_val <= new_cost:
                    dominated = True
                    break
                # If new state dominates (i.e., is better in all criteria) an existing state, mark existing state for removal.
                if new_latency <= lat and new_survival >= surv and new_cost <= cost_val:
                    indices_to_remove.append(idx)
            if dominated:
                continue
            # Remove dominated states.
            for idx in sorted(indices_to_remove, reverse=True):
                dp[neighbor].pop(idx)
            dp[neighbor].append(new_state)
            
            heapq.heappush(heap, (new_cost, neighbor, new_latency, new_survival))
    return -1