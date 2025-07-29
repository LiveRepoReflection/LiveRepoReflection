import bisect

def solve_max_profit_scheduling(tasks):
    # Filter out invalid tasks where start_time > end_time.
    valid_tasks = [task for task in tasks if task[0] <= task[1]]
    if not valid_tasks:
        return 0

    # Sort tasks by their end time.
    valid_tasks.sort(key=lambda x: x[1])
    end_times = [task[1] for task in valid_tasks]
    n = len(valid_tasks)
    
    # Initialize dynamic programming table.
    dp = [0] * n
    dp[0] = valid_tasks[0][2]
    
    for i in range(1, n):
        start, end, profit = valid_tasks[i]
        # Option 1: Exclude the current task.
        option1 = dp[i - 1]
        # Option 2: Include the current task.
        # Find the index of the last task that doesn't conflict.
        index = bisect.bisect_right(end_times, start) - 1
        option2 = profit
        if index != -1:
            option2 += dp[index]
        dp[i] = max(option1, option2)
    
    return dp[-1]