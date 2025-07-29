import bisect

def max_billboard_revenue(L, N, T, x, r):
    if N == 0:
        return 0

    # Create list of tuples and sort by location
    billboards = sorted(zip(x, r), key=lambda item: item[0])
    sorted_x = [loc for loc, _ in billboards]
    revenues = [rev for _, rev in billboards]
    
    dp = [0] * (N + 1)
    
    # Iterate from the last billboard backwards
    for i in range(N - 1, -1, -1):
        # Find the first billboard index j such that its location is >= current location + T
        next_index = bisect.bisect_left(sorted_x, sorted_x[i] + T)
        take_revenue = revenues[i] + (dp[next_index] if next_index < N else 0)
        skip_revenue = dp[i + 1]
        dp[i] = max(take_revenue, skip_revenue)
    
    return dp[0]