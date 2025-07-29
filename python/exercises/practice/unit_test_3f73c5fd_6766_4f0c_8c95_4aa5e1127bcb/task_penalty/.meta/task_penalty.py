from functools import lru_cache

def task_penalty(tasks):
    # Number of tasks
    n = len(tasks)
    if n == 0:
        return 0

    # Create a mapping from task id to its index
    id_to_index = {}
    for i, (tid, duration, deadline, penalty, dependencies) in enumerate(tasks):
        id_to_index[tid] = i

    # Standardize each task to a tuple: (id, duration, deadline, penalty, dependency_indices)
    T = []
    for (tid, duration, deadline, penalty, dependencies) in tasks:
        dep_indices = [id_to_index[d] for d in dependencies]
        T.append((tid, duration, deadline, penalty, dep_indices))

    @lru_cache(maxsize=None)
    def dp(mask, current_time):
        if mask == (1 << n) - 1:
            return 0

        best = float('inf')
        for i in range(n):
            if mask & (1 << i):
                continue
            # Check all dependencies for task i have been completed.
            _, duration, deadline, penalty, dep_indices = T[i]
            valid = True
            for d in dep_indices:
                if not (mask & (1 << d)):
                    valid = False
                    break
            if not valid:
                continue

            new_time = current_time + duration
            add_penalty = penalty if new_time > deadline else 0
            new_mask = mask | (1 << i)
            candidate = dp(new_mask, new_time) + add_penalty
            best = min(best, candidate)
        return best

    return dp(0, 0)