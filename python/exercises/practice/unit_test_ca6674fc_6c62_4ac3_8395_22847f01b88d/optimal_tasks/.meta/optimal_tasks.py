def minimum_cost(N, cost, deadline, dependencies):
    # Precompute for each task, the bitmask of its dependencies.
    dep_mask = [0] * N
    for i in range(N):
        for d in dependencies[i]:
            dep_mask[i] |= (1 << d)

    best = None

    # Function to check if a subset (represented by bitmask s) is closed under dependencies
    def is_closed(s):
        # For each task i in s, all dependencies must be in s.
        # If any task i in s has a dependency not in s, return False.
        m = s
        while m:
            i = (m & -m).bit_length() - 1
            if (dep_mask[i] & s) != dep_mask[i]:
                return False
            m &= m - 1
        return True

    # For a given closed subset s, check if there exists a valid topological ordering
    # that also meets the deadlines. We use DFS with memoization.
    def can_schedule(s):
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def dfs(scheduled, cumulative_time):
            if scheduled == s:
                return True
            # For each task in s that is not scheduled and whose dependencies are all scheduled
            for i in range(N):
                if (s >> i) & 1 and not (scheduled >> i) & 1:
                    # Check if all dependencies of i are in scheduled.
                    if (dep_mask[i] & scheduled) != dep_mask[i]:
                        continue
                    next_time = cumulative_time + cost[i]
                    if next_time > deadline[i]:
                        continue
                    # Mark this task as scheduled and continue DFS.
                    if dfs(scheduled | (1 << i), next_time):
                        return True
            return False

        return dfs(0, 0)

    # Iterate over all non-empty subsets s of tasks.
    # Since N <= 20, 1 << N iterations is feasible.
    for s in range(1, 1 << N):
        # First, check if s is closed under dependencies.
        if not is_closed(s):
            continue
        # Check if the tasks in this closed subset can be scheduled meeting deadlines.
        if can_schedule(s):
            # The total cost for subset s is the sum of cost of tasks in s.
            subset_cost = 0
            temp = s
            while temp:
                i = (temp & -temp).bit_length() - 1
                subset_cost += cost[i]
                temp &= temp - 1
            if best is None or subset_cost < best:
                best = subset_cost

    return best if best is not None else -1

if __name__ == "__main__":
    # Example run for manual testing.
    # You can run this file to manually test the function.
    N = 4
    cost = [5, 3, 8, 4]
    deadline = [10, 12, 15, 20]
    dependencies = [
        [],     # Task 0
        [0],    # Task 1
        [0, 1], # Task 2
        [2]     # Task 3
    ]
    result = minimum_cost(N, cost, deadline, dependencies)
    print(result)