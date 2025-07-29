import heapq

def min_delivery_cost(city_graph, delivery_orders):
    def find_min_cost(start, end, deadline):
        # Each state: (total_cost, total_time, node)
        heap = [(0, 0, start)]
        # For each node, store list of (time, cost) labels that are non-dominated
        labels = {node: [] for node in city_graph}
        labels[start].append((0, 0))
        
        while heap:
            cost, time, node = heapq.heappop(heap)
            if time > deadline:
                continue
            if node == end:
                return cost
            # Explore neighbors
            for neighbor, travel_time, edge_cost in city_graph.get(node, []):
                new_time = time + travel_time
                new_cost = cost + edge_cost
                if new_time > deadline:
                    continue
                # Check if new state is dominated for neighbor
                dominated = False
                indices_to_remove = []
                for idx, (t, c) in enumerate(labels.get(neighbor, [])):
                    # if existing state is as good or better, skip new state
                    if t <= new_time and c <= new_cost:
                        dominated = True
                        break
                    # else if new state dominates an existing state, mark that index for removal
                    if new_time <= t and new_cost <= c:
                        indices_to_remove.append(idx)
                if dominated:
                    continue
                # Remove dominated states
                if neighbor not in labels:
                    labels[neighbor] = []
                # Remove indices in reverse order to avoid shifting
                for idx in sorted(indices_to_remove, reverse=True):
                    labels[neighbor].pop(idx)
                labels[neighbor].append((new_time, new_cost))
                heapq.heappush(heap, (new_cost, new_time, neighbor))
        return None

    total_cost = 0
    for start, end, deadline in delivery_orders:
        # If order is from a node not in graph, consider it infeasible.
        if start not in city_graph or end not in city_graph:
            continue
        if start == end and deadline >= 0:
            total_cost += 0
            continue
        result = find_min_cost(start, end, deadline)
        if result is not None:
            total_cost += result
    return total_cost