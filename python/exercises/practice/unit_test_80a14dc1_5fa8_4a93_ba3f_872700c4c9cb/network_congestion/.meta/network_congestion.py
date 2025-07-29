def assign_users(N, M, C, D, K):
    # Quick check: if any user's data exceeds the maximum server capacity,
    # no assignment is possible.
    if max(D) > max(C):
        return None

    # Prepare indexed users sorted in descending order by data volume.
    users = sorted([(D[i], i) for i in range(M)], key=lambda x: x[0], reverse=True)

    # Global variable to store a feasible assignment (in sorted order)
    best_assignment_sorted = None

    # DFS backtracking to try to assign users to servers within capacity limits.
    def can_assign(idx, capacities, current_assignment):
        nonlocal best_assignment_sorted
        if idx == len(users):
            best_assignment_sorted = list(current_assignment)
            return True
        volume, _ = users[idx]
        prev = -1.0  # used to skip duplicate capacities to prune search
        for server in range(N):
            # Prune if the same capacity value was already used in this branch.
            if capacities[server] < volume - 1e-9:
                continue
            if abs(capacities[server] - prev) < 1e-9:
                continue
            prev = capacities[server]
            capacities[server] -= volume
            current_assignment.append(server)
            if can_assign(idx + 1, capacities, current_assignment):
                return True
            current_assignment.pop()
            capacities[server] += volume
        return False

    # Check feasibility for given latency L.
    def feasible(L):
        # Determine allowed load for each server.
        allowed = []
        # When L < 1, allowed load is C[i]*L^(1/K), otherwise capacity is the limit.
        # Note: L might be 0, so we handle that separately.
        for cap in C:
            if L < 1:
                allowed.append(cap * (L ** (1 / K)))
            else:
                allowed.append(cap)
        # Quick check: if any user's data exceeds all allowed capacities, return False.
        for vol, _ in users:
            if all(allowed[i] + 1e-9 < vol for i in range(N)):
                return False

        # Use DFS to check if we can assign users (in sorted order) to servers given allowed loads.
        nonlocal best_assignment_sorted
        best_assignment_sorted = None
        if can_assign(0, allowed, []):
            return True
        return False

    # Binary search to minimize maximum latency.
    # The latency for any server is at most 1 when a server reaches its capacity.
    lo = 0.0
    hi = 1.0
    eps = 1e-6
    feasible_assignment = None

    # First, check if assignment is possible at L = 1. It must be possible if overall capacity suffices.
    if not feasible(hi):
        return None

    # Binary search loop.
    while hi - lo > eps:
        mid = (lo + hi) / 2.0
        if feasible(mid):
            hi = mid
            # Save the solution found in DFS for later reconstruction.
            feasible_assignment = list(best_assignment_sorted)  
        else:
            lo = mid

    # If for some reason we didn't capture an assignment, run feasibility one last time.
    if feasible_assignment is None:
        if feasible(hi):
            feasible_assignment = list(best_assignment_sorted)
        else:
            return None

    # Reconstruct the assignment in terms of original user indices.
    # best_assignment_sorted is aligned with users sorted descending.
    assignment = [None] * M
    for pos, (_, orig_index) in enumerate(users):
        assignment[orig_index] = feasible_assignment[pos]
    return assignment

if __name__ == "__main__":
    # Simple manual test in case needed.
    N = 3
    M = 5
    C = [80, 100, 60]
    D = [20, 30, 40, 10, 20]
    K = 2.5
    result = assign_users(N, M, C, D, K)
    print(result)