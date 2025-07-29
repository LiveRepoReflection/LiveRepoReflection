from bisect import bisect_right

def approximate_median(worker_data, epsilon):
    # Preprocess worker data: sort each worker's list if not empty.
    sorted_workers = []
    for data in worker_data:
        if data:
            sorted_workers.append(sorted(data))
    if not sorted_workers:
        return None

    # Compute total count, global min, and global max.
    total_count = 0
    global_min = None
    global_max = None
    for data in sorted_workers:
        total_count += len(data)
        local_min = data[0]
        local_max = data[-1]
        if global_min is None or local_min < global_min:
            global_min = local_min
        if global_max is None or local_max > global_max:
            global_max = local_max

    if total_count == 0:
        return None

    # Determine target rank for the median.
    # For an odd count, it's the middle element; for an even count,
    # we choose the lower median (as per integer return expectation).
    target = (total_count + 1) // 2

    # Tolerance in terms of count deviation.
    tolerance = int(epsilon * total_count)

    # Define a function to compute rank: count of numbers <= x across all workers.
    def rank(x):
        cnt = 0
        for data in sorted_workers:
            cnt += bisect_right(data, x)
        return cnt

    # Binary search on the integer range [global_min, global_max]
    low, high = global_min, global_max
    candidate = None
    while low <= high:
        mid = (low + high) // 2
        r = rank(mid)
        if r < target:
            low = mid + 1
        else:
            candidate = mid
            high = mid - 1

    if candidate is None:
        candidate = global_min

    # Check candidate error and consider neighbor candidate candidate-1 if possible.
    candidate_error = abs(rank(candidate) - target)
    best_candidate = candidate
    best_error = candidate_error

    if candidate > global_min:
        alt = candidate - 1
        alt_error = abs(rank(alt) - target)
        if alt_error < best_error:
            best_candidate = alt
            best_error = alt_error

    # For epsilon=0, we insist on an exact match.
    if epsilon == 0 and best_error != 0:
        # When no exact median is found, we return the candidate with exact rank if possible.
        # Re-run binary search for exact match: this may only succeed if such a number exists.
        low, high = global_min, global_max
        exact_candidate = None
        while low <= high:
            mid = (low + high) // 2
            r = rank(mid)
            if r == target:
                exact_candidate = mid
                break
            elif r < target:
                low = mid + 1
            else:
                high = mid - 1
        if exact_candidate is not None:
            best_candidate = exact_candidate
            best_error = 0

    # Verify that the chosen candidate is within tolerance.
    if best_error <= tolerance:
        return best_candidate
    # In the unlikely event that no candidate satisfies the tolerance,
    # return the candidate with the minimal error.
    return best_candidate