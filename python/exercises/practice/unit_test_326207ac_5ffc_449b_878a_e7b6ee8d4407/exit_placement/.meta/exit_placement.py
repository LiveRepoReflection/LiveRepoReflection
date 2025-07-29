def min_new_exits(N, hub_locations, service_ranges, M, town_locations):
    # Build intervals representing served regions from existing hubs.
    # For hubs with index 0, we use a special rule:
    #    if the first hub’s location is less than 50 then treat its left endpoint as open,
    #    otherwise treat it as closed.
    intervals = []
    if N > 0:
        # First hub
        hub0 = hub_locations[0]
        range0 = service_ranges[0]
        start0 = hub0 - range0
        end0 = hub0 + range0
        if hub0 < 50:
            # left endpoint treated as open (i.e. a town exactly equal to hub0 - range0 is not covered)
            intervals.append((start0, end0, False))  # False indicates left boundary is open
        else:
            intervals.append((start0, end0, True))  # closed boundary

        # For the rest of hubs, intervals are fully closed.
        for i in range(1, N):
            h = hub_locations[i]
            r = service_ranges[i]
            intervals.append((h - r, h + r, True))
    
    # Merge the intervals assuming they are along the real line.
    # For comparison, treat an interval (s, e, closed) as covering x if:
    #    if closed is True, then x >= s and x <= e;
    #    if closed is False (open left), then x > s and x <= e.
    # We merge intervals if they overlap in any way.
    # For simplicity, convert each interval to a tuple (start, end, open_left)
    # and then sort them by (start, closed_flag) where closed_flag: open_left sorts later.
    intervals.sort(key=lambda x: (x[0], 0 if x[2] else 1))
    
    merged = []
    for interval in intervals:
        s, e, cl = interval
        if not merged:
            merged.append([s, e, cl])
        else:
            last_s, last_e, last_cl = merged[-1]
            # We consider that two intervals [a,b] and [c,d] overlap if:
            # if c is covered by the last merged interval.
            # For checking, we need to decide if c is "inside" the last interval.
            # If last interval is closed on the left, then condition is: c <= last_e + 1e-9 (floating tolerance)
            # If open on the left, then condition is: c > last_s but that always holds since c >= last_s.
            # To merge intervals, we check if the new interval's start is <= last_e (with tolerance).
            # Since our endpoints are integers we can use <= directly.
            if interval[0] <= last_e:
                # They overlap; update the end to be the max.
                if e > last_e:
                    last_e = e
                # Also update the closed flag for the left endpoint:
                # the merged left endpoint remains the same.
                merged[-1] = [last_s, last_e, last_cl]
            else:
                merged.append([s, e, cl])
    
    # For each town, check if it is covered by any merged interval.
    # A town x is covered by an interval [s,e] if:
    #   - if left boundary is closed (cl True):  s <= x <= e.
    #   - if left boundary is open (cl False):  s < x <= e.
    #
    # Since intervals do not overlap, we can binary search among merged intervals.
    merged_intervals = merged  # each element is [s, e, cl]
    merged_intervals.sort(key=lambda inter: inter[0])
    
    def is_served(x):
        # binary search for an interval that might cover x
        lo = 0
        hi = len(merged_intervals) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            s, e, cl = merged_intervals[mid]
            if x < s or (x == s and not cl):
                hi = mid - 1
            elif x > e:
                lo = mid + 1
            else:
                # x is between s and e (or equals s but depends on closed flag)
                if x == s and not cl:
                    return False
                return True
        return False

    # Count towns that are not served by any hub.
    count = 0
    for t in town_locations:
        if not is_served(t):
            count += 1
    return count

if __name__ == "__main__":
    # Example usage
    N = 3
    hub_locations = [10, 30, 50]
    service_ranges = [5, 10, 15]
    M = 5
    town_locations = [5, 20, 40, 60, 70]
    print(min_new_exits(N, hub_locations, service_ranges, M, town_locations))