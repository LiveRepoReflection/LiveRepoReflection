import math

def min_total_cost(n, k, adj_list, workload):
    if k > n:
        return -1

    # Precompute shortest path distances using Floyd Warshall.
    dist = [[math.inf] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
        for j in adj_list[i]:
            dist[i][j] = 1
            # Since graph is undirected.
            dist[j][i] = 1

    for m in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][m] + dist[m][j] < dist[i][j]:
                    dist[i][j] = dist[i][m] + dist[m][j]

    # Global minimum cost
    best_cost = [math.inf]

    # Recursive function to generate all partitions.
    # clusters: list of clusters, each cluster is a list of node indices.
    def backtrack(idx, clusters):
        if idx == n:
            if len(clusters) == k:
                cost = compute_partition_cost(clusters)
                if cost < best_cost[0]:
                    best_cost[0] = cost
            return
        # Try to add node idx to each existing cluster.
        for i in range(len(clusters)):
            clusters[i].append(idx)
            backtrack(idx + 1, clusters)
            clusters[i].pop()
        # Try to create a new cluster if we haven't reached k clusters yet.
        if len(clusters) < k:
            clusters.append([idx])
            backtrack(idx + 1, clusters)
            clusters.pop()

    # Compute cost of a given partition.
    def compute_partition_cost(clusters):
        total = 0
        # Intra-cluster communication cost.
        for cluster in clusters:
            intra = 0
            size = len(cluster)
            for i in range(size):
                for j in range(i + 1, size):
                    intra += workload[cluster[i]] * workload[cluster[j]]
            total += intra

        # Inter-cluster latency penalty.
        num_clusters = len(clusters)
        for i in range(num_clusters):
            for j in range(i + 1, num_clusters):
                sum1 = sum(workload[node] for node in clusters[i])
                sum2 = sum(workload[node] for node in clusters[j])
                min_latency = math.inf
                for u in clusters[i]:
                    for v in clusters[j]:
                        if dist[u][v] < min_latency:
                            min_latency = dist[u][v]
                if min_latency == math.inf:
                    # If no connection exists for any pair, treat this partition as invalid.
                    return math.inf
                total += min_latency * sum1 * sum2
        return total

    backtrack(0, [])
    return best_cost[0] if best_cost[0] != math.inf else -1

if __name__ == '__main__':
    # For simple direct testing:
    # Example: n = 4, k = 2, adj_list = [[1], [0, 2], [1, 3], [2]], workload = [10, 5, 8, 2]
    n = 4
    k = 2
    adj_list = [[1], [0, 2], [1, 3], [2]]
    workload = [10, 5, 8, 2]
    result = min_total_cost(n, k, adj_list, workload)
    print(result)