def assign_requests(N, requests, capacities, latencies, request_data_sources):
    # Determine the number of data sources from the latencies matrix.
    M = len(latencies[0]) if latencies and latencies[0] else 0

    # Precompute sorted worker indices for each data source based on latency.
    sorted_workers = {}
    for ds in range(M):
        sorted_workers[ds] = sorted(range(N), key=lambda i: latencies[i][ds])

    # Initialize the result list for each worker and track assigned counts.
    result = [[] for _ in range(N)]
    assigned_count = [0] * N

    # Process each request in its original order.
    for req, ds in zip(requests, request_data_sources):
        # Iterate over workers sorted by latency for this data source.
        for worker in sorted_workers.get(ds, []):
            if assigned_count[worker] < capacities[worker]:
                result[worker].append(req)
                assigned_count[worker] += 1
                break

    return result

if __name__ == "__main__":
    # This main block is for simple local testing and debugging.
    # It will not be executed during unit tests.
    N = 2
    requests = ["req1", "req2", "req3", "req4"]
    capacities = [3, 3]
    latencies = [
        [10, 20],
        [15, 5]
    ]
    request_data_sources = [0, 0, 1, 1]
    assignment = assign_requests(N, requests, capacities, latencies, request_data_sources)
    print(assignment)