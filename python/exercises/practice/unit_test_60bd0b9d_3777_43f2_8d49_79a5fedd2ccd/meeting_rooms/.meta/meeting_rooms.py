def meeting_rooms(employees, meeting_requests):
    # Precompute free intervals for each employee given their busy intervals.
    # Busy intervals: list of (start, end)
    # Free intervals: list of (start, end) where end is exclusive.
    def compute_free_intervals(busy):
        busy_sorted = sorted(busy, key=lambda x: x[0])
        free = []
        current = 0
        for s, e in busy_sorted:
            if s > current:
                free.append((current, s))
            current = max(current, e)
        if current < 1440:
            free.append((current, 1440))
        return free

    # Given two lists of intervals (each as (start, end)), return their intersection.
    def intersect_intervals(list1, list2):
        i, j = 0, 0
        result = []
        while i < len(list1) and j < len(list2):
            a1, b1 = list1[i]
            a2, b2 = list2[j]
            # Intersection
            start = max(a1, a2)
            end = min(b1, b2)
            if start < end:
                result.append((start, end))
            if b1 < b2:
                i += 1
            else:
                j += 1
        return result

    # From a given interval [s, e] in free time, the meeting of duration d can start anytime in [s, e-d]
    # We return the feasible start range if possible.
    def feasible_start_intervals(intervals, d):
        result = []
        for a, b in intervals:
            if b - a >= d:
                # interval in which meeting can start is [a, b - d]
                result.append((a, b - d))
        return result

    # For a meeting with feasible start intervals F (list of (start, end)) and duration d,
    # given that we want to start no earlier than L, if there is an option,
    # return the earliest possible start time >= L. Otherwise, return None.
    def find_start_time(feasible_intervals, L, d):
        # feasible_intervals is sorted by start time and non overlapping.
        for a, b in feasible_intervals:
            if L <= b:
                candidate = L if L >= a else a
                if candidate <= b:
                    return candidate
        return None

    # Precompute free intervals for each employee.
    employee_free = []
    for busy in employees:
        employee_free.append(compute_free_intervals(busy))

    # For each meeting request, compute the feasible start intervals (list of (start, end)) based on the intersection
    # of free intervals of all required participants.
    meetings = []
    for req in meeting_requests:
        participants, duration = req
        # Start with overall day free interval.
        common = [(0, 1440)]
        for pid in participants:
            common = intersect_intervals(common, employee_free[pid])
            if not common:
                break  # No feasible free time for these participants.
        feasible = feasible_start_intervals(common, duration)
        # If no feasible start interval, meeting is unschedulable.
        if not feasible:
            # As per the problem, assume all meetings are schedulable.
            raise ValueError("Meeting request unschedulable with given employee calendars")
        # For sorting purposes, get the earliest finish time possible if scheduled as early as possible.
        earliest_start = feasible[0][0]
        meetings.append({
            'feasible': feasible,  # list of (start, end) intervals for start times
            'duration': duration,
            'min_finish': earliest_start + duration
        })

    # Sort meetings by their earliest finish time if started at the earliest possible start.
    meetings.sort(key=lambda m: m['min_finish'])

    # For each meeting, try to schedule it in one of the existing rooms.
    # Each room is represented by the finish time of the last scheduled meeting.
    rooms = []

    for meeting in meetings:
        duration = meeting['duration']
        feasible = meeting['feasible']
        best_room_index = None
        best_start = None
        best_finish = None
        # Try each room: room is available from a certain time.
        for i in range(len(rooms)):
            available_time = rooms[i]
            start_time = find_start_time(feasible, available_time, duration)
            if start_time is not None:
                finish_time = start_time + duration
                # Choose the room where meeting finishes the earliest.
                if best_finish is None or finish_time < best_finish:
                    best_finish = finish_time
                    best_start = start_time
                    best_room_index = i
        if best_room_index is not None:
            # Schedule meeting in that room.
            rooms[best_room_index] = best_finish
        else:
            # No existing room could accommodate meeting;
            # schedule in a new room starting at the earliest possible start time.
            start_time = find_start_time(feasible, 0, duration)
            finish_time = start_time + duration
            rooms.append(finish_time)

    return len(rooms)


if __name__ == '__main__':
    # For quick local testing
    # Example scenario
    employees = [
        [(60, 120), (300, 360)],  # Employee 0 busy intervals
        [(180, 240)],             # Employee 1 busy intervals
        [(420, 480)]              # Employee 2 busy intervals
    ]
    meeting_requests = [
        ([0, 1], 60),
        ([1, 2], 120)
    ]
    print(meeting_rooms(employees, meeting_requests))