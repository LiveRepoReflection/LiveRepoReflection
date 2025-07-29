import bisect
import math

def process_median_stream(N, epsilon, data_streams, queries):
    # Initialize worker data structures: each worker maintains a sorted list.
    workers = [[] for _ in range(N)]
    # Pointers for each worker's data stream
    pointers = [0] * N
    # Total number of data points processed so far
    global_time = 0

    # Prepare queries with their original order, though we assume queries are in increasing order.
    query_indices = list(range(len(queries)))
    sorted_queries = sorted(zip(queries, query_indices), key=lambda x: x[0])
    query_results = [None] * len(queries)
    current_query_idx = 0

    # Function to compute median exactly from a merged sorted list
    def compute_median(merged):
        n = len(merged)
        if n % 2 == 1:
            return float(merged[n // 2])
        else:
            return (merged[n // 2 - 1] + merged[n // 2]) / 2.0

    # Function to merge sorted lists efficiently
    def merge_workers(workers_lists):
        merged = []
        for lst in workers_lists:
            merged.extend(lst)
        merged.sort()
        return merged

    # Simulate processing in round-robin order
    # Continue until all data is processed or all queries are answered
    while current_query_idx < len(sorted_queries):
        # Check if we still have any data in any worker's stream
        data_processed_in_round = False
        for i in range(N):
            if pointers[i] < len(data_streams[i]):
                # Process one element from worker i
                value = data_streams[i][pointers[i]]
                pointers[i] += 1
                global_time += 1
                # Insert the value in sorted order into worker's local summary
                bisect.insort(workers[i], value)
                data_processed_in_round = True
                # Handle any queries that occur at this time stamp
                while current_query_idx < len(sorted_queries) and sorted_queries[current_query_idx][0] == global_time:
                    merged = merge_workers(workers)
                    median_val = compute_median(merged)
                    # Since exact median is computed, the error is 0 which is within any epsilon.
                    query_time, original_idx = sorted_queries[current_query_idx]
                    query_results[original_idx] = median_val
                    current_query_idx += 1
        # If no data was processed in this round, break (should not happen if queries are valid)
        if not data_processed_in_round:
            break

    return query_results