import math

def optimize_cdn(routers, user_requests, content_items, capacity, latency_matrix):
    # Determine the closest router for each user request using Euclidean distance.
    # routers: list of (lat, lon) for edge routers
    # user_requests: list of ((lat, lon), frequency)
    # We'll assign each user request to the closest router (by Euclidean distance).
    # Build a mapping: router index -> total frequency from its assigned requests.
    num_routers = len(routers)
    router_request_freq = [0] * num_routers

    for (u_lat, u_lon), freq in user_requests:
        min_dist = float('inf')
        closest_idx = None
        for idx, (r_lat, r_lon) in enumerate(routers):
            dist = math.hypot(u_lat - r_lat, u_lon - r_lon)
            if dist < min_dist:
                min_dist = dist
                closest_idx = idx
        router_request_freq[closest_idx] += freq

    # For each router, decide which content items to store using a knapsack approach.
    # For each router, the "value" of storing a content item j is:
    # value = (total frequency of user requests for that router) * (popularity of j) *
    #         (latency between central repo (index 0) and this router (index i+1))
    # The "cost" is the size of the content item.
    # We then pick the subset that maximizes total value while the total size is <= capacity.
    
    # Define knapsack solver that returns the set of selected item indices.
    def knapsack(values, weights, capacity):
        n = len(values)
        # dp[i][w]: maximum value using items 0..(i-1) with total weight <= w.
        dp = [[0]*(capacity+1) for _ in range(n+1)]
        # keep track of choices
        for i in range(1, n+1):
            wt = weights[i-1]
            val = values[i-1]
            for w in range(capacity+1):
                if wt > w:
                    dp[i][w] = dp[i-1][w]
                else:
                    dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt] + val)
        
        # Reconstruct selected indices
        selected = set()
        w = capacity
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected.add(i-1)
                w -= weights[i-1]
        return selected

    placement = []
    for router_idx in range(num_routers):
        total_freq = router_request_freq[router_idx]
        # For current router, if there are no user requests, value of storing content is 0.
        # However, we still can store items if desired but it's not beneficial.
        values = []
        weights = []
        for j, (size, popularity) in enumerate(content_items):
            # Value is computed as the saving in latency for serving a request locally rather than fetching from central.
            # Saving per request for router: latency_matrix[router_index+1][0] (central to router latency).
            # Multiply by the total number of requests and the content popularity factor.
            saving = latency_matrix[router_idx+1][0]
            value = total_freq * popularity * saving
            values.append(value)
            weights.append(size)
        # Use knapsack to decide which content items to store at this router.
        selected_contents = knapsack(values, weights, capacity)
        placement.append(selected_contents)

    return placement