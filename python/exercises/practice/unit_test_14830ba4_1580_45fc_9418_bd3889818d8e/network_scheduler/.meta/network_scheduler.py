import collections
import copy

def network_scheduler(n, links, jobs, current_time):
    # Build initial residual network from undirected links
    # Represent residual network as a dictionary of dictionaries: residual[u][v] = capacity
    residual = {u: {} for u in range(n)}
    for u, v, capacity in links:
        if v not in residual[u]:
            residual[u][v] = 0
        if u not in residual[v]:
            residual[v][u] = 0
        residual[u][v] += capacity
        residual[v][u] += capacity

    # Helper function: BFS to find an augmenting path in residual network from s to t.
    def bfs(rnet, s, t):
        parent = {u: None for u in rnet}
        visited = set()
        queue = collections.deque()
        queue.append(s)
        visited.add(s)
        while queue:
            u = queue.popleft()
            if u == t:
                break
            for v in rnet[u]:
                if v not in visited and rnet[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
                    if v == t:
                        break
        if parent[t] is None:
            return None
        # Reconstruct path from s to t
        path = []
        cur = t
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path

    # Function to send flow along the found path in the provided residual network copy.
    # Returns the bottleneck value along the path.
    def send_flow(rnet, path, flow):
        bottleneck = flow
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            if rnet[u][v] < bottleneck:
                bottleneck = rnet[u][v]
        # Update capacities along the path
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            rnet[u][v] -= bottleneck
            # Increase reverse flow; create key if necessary
            if u not in rnet[v]:
                rnet[v][u] = 0
            rnet[v][u] += bottleneck
        return bottleneck

    # Filter out expired jobs
    valid_jobs = []
    for idx, job in enumerate(jobs):
        s, d, b, t, p = job
        if t > current_time:
            valid_jobs.append((idx, s, d, b, t, p))
    # Sort jobs: prioritize by descending priority, then by earlier deadline
    valid_jobs.sort(key=lambda x: (-x[5], x[4]))

    scheduled_jobs = []

    # Process each job greedily on a copy of the residual network
    for job in valid_jobs:
        idx, s, d, required_bandwidth, t_deadline, priority = job
        # Clone current residual network for tentative scheduling of this job.
        temp_residual = copy.deepcopy(residual)
        remaining = required_bandwidth
        # Attempt to send flow until requirement is met
        while remaining > 0:
            path = bfs(temp_residual, s, d)
            if path is None:
                # Unable to satisfy this job; break out and do not commit changes.
                break
            # Determine possible flow along the found path.
            flow_sent = send_flow(temp_residual, path, remaining)
            remaining -= flow_sent
        if remaining <= 0:
            # Job accomplished; update the main residual network 
            residual = temp_residual
            scheduled_jobs.append(idx)
            
    # Return scheduled job indices sorted in ascending order.
    return sorted(scheduled_jobs)