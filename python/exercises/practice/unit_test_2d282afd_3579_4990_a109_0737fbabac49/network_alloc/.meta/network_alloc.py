from collections import deque

def network_alloc(N, edge_data, requests, reduction):
    factor = (100.0 - reduction) / 100.0
    graph_adj = [[] for _ in range(N)]
    edge_list = []
    for (u, v, cap) in edge_data:
        edge_index = len(edge_list)
        edge_list.append([u, v, float(cap)])
        graph_adj[u].append(edge_index)
    
    satisfied_count = 0

    for (s, d, req) in requests:
        req_amount = float(req)
        prev = [-1] * N
        visited = [False] * N
        queue = deque()
        visited[s] = True
        queue.append(s)
        found = False

        while queue and not found:
            curr = queue.popleft()
            for edge_idx in graph_adj[curr]:
                u, v, cap = edge_list[edge_idx]
                if cap + 1e-9 >= req_amount and not visited[v]:
                    visited[v] = True
                    prev[v] = edge_idx
                    if v == d:
                        found = True
                        break
                    queue.append(v)
        
        if found:
            node = d
            path_edges = []
            while node != s:
                edge_index = prev[node]
                path_edges.append(edge_index)
                node = edge_list[edge_index][0]
            for edge_idx in path_edges:
                edge_list[edge_idx][2] -= req_amount
            satisfied_count += 1
        
        for i in range(len(edge_list)):
            edge_list[i][2] *= factor
            if edge_list[i][2] < 1e-9:
                edge_list[i][2] = 0.0

    return satisfied_count

if __name__ == "__main__":
    import sys
    data = sys.stdin.read().strip().split()
    if not data:
        exit(0)
    it = iter(data)
    N = int(next(it))
    E = int(next(it))
    R = int(next(it))
    reduction = float(next(it))
    edges = []
    for _ in range(E):
        u = int(next(it))
        v = int(next(it))
        cap = int(next(it))
        edges.append((u, v, cap))
    requests = []
    for _ in range(R):
        s = int(next(it))
        d = int(next(it))
        req = float(next(it))
        requests.append((s, d, req))
    print(network_alloc(N, edges, requests, reduction))