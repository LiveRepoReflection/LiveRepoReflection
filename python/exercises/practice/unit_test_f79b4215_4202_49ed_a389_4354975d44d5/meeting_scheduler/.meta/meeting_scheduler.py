def meeting_scheduler(employees, hierarchy, attendees, duration):
    # Build a common availability array (length 168) representing half-hour slots
    # common[t] is True if all attendees are available at time t (0 <= t < 168)
    common = [True] * 168
    for att in attendees:
        emp_availability = [False] * 168
        # Mark the availability for each attendee based on their intervals
        for interval in employees.get(att, []):
            start, end = interval
            # Mark time slots from start (inclusive) to end (exclusive)
            for t in range(start, end):
                if 0 <= t < 168:
                    emp_availability[t] = True
        # Combine using logical AND for the common availability
        for t in range(168):
            common[t] = common[t] and emp_availability[t]

    # Identify all candidate start times where 'duration' consecutive slots are available
    candidates = []
    for start in range(168 - duration + 1):
        valid = True
        for t in range(start, start + duration):
            if not common[t]:
                valid = False
                break
        if valid:
            candidates.append(start)

    if not candidates:
        return None

    # Compute the set of affected employees:
    # For each attendee, all employees that are direct or indirect reports are considered affected.
    affected = set()

    # Helper function for DFS through hierarchy
    def dfs(emp, visited, affected_set):
        for sub in hierarchy.get(emp, []):
            if sub not in visited:
                visited.add(sub)
                affected_set.add(sub)
                dfs(sub, visited, affected_set)

    for att in attendees:
        affected_set = set()
        visited = set()
        dfs(att, visited, affected_set)
        affected.update(affected_set)
    # Exclude employees who are attendees themselves
    affected -= set(attendees)

    # Function to compute interruption score for a meeting slot [start, end)
    # The score is the count of affected employees that have any availability overlapping with the meeting.
    def compute_score(start, end):
        score = 0
        for emp in affected:
            for interval in employees.get(emp, []):
                s, e = interval
                # Determine if there is an overlap between [start, end) and [s, e)
                if max(start, s) < min(end, e):
                    score += 1
                    break  # Count each employee at most once
        return score

    # Iterate through candidate start times (sorted in ascending order) to find the optimal meeting slot.
    best_score = None
    best_start = None
    for start in candidates:
        end = start + duration
        score = compute_score(start, end)
        if best_score is None or score < best_score:
            best_score = score
            best_start = start

    if best_start is None:
        return None
    return (best_start, best_start + duration)


if __name__ == "__main__":
    # Sample manual test using the provided example
    employees = {
        1: [(0, 4), (8, 12)],
        2: [(2, 6), (10, 14)],
        3: [(0, 2), (4, 6)],
        4: [(10, 12)]
    }
    hierarchy = {
        1: [2, 3],
        2: [4],
        3: []
    }
    attendees = [1, 2, 4]
    duration = 2
    result = meeting_scheduler(employees, hierarchy, attendees, duration)
    print("Meeting Slot:", result)