def schedule_conference(talks, rooms, conferenceDuration, K, penaltyFactor):
    """
    Schedules talks into available rooms to maximize the total effective attendance points.
    The effective attendance of a talk may be penalized if the unique keyword diversity in the 
    corresponding time segments is below K.

    This implementation uses a greedy heuristic:
    1. Sort talks by start time.
    2. For each talk, assign it to the room that becomes free the earliest, provided the talk does 
       not overlap with the last talk scheduled in that room.
    3. The penalty factor is not used in the assignment decision but could be used in a post-hoc 
       evaluation of the schedule's effective score. This heuristic does not guarantee a true global
       optimum but offers a reasonable trade-off between scheduling feasibility and effective attendance.

    Parameters:
        talks (list of dict): Each dict has keys:
            - 'id': unique identifier of the talk.
            - 'startTime': start time in minutes.
            - 'endTime': end time in minutes.
            - 'expectedAttendance': estimated attendee count.
            - 'keywords': list of associated keywords.
        rooms (list of dict): Each dict has key 'id' to uniquely identify a room.
        conferenceDuration (int): Total duration of the conference in minutes.
        K (int): Minimum unique keyword count required in any timeslot.
        penaltyFactor (float): Factor by which attendance is penalized if keyword diversity condition is not met.
    
    Returns:
        dict: A dictionary mapping each room's id to a list of scheduled talk ids (sorted by start time).
    """
    # Create a dictionary for schedules for each room
    schedule = {room['id']: [] for room in rooms}
    # Keep track of the end time of the last talk scheduled in each room.
    room_end_time = {room['id']: 0 for room in rooms}
    
    # Sort talks by start time (earliest first)
    sorted_talks = sorted(talks, key=lambda t: t['startTime'])
    
    # Greedily try to assign each talk to a room without causing overlapping events.
    for talk in sorted_talks:
        assigned = False
        # Try rooms ordered by the earliest available end_time to maximize room usage.
        sorted_rooms = sorted(rooms, key=lambda r: room_end_time[r['id']])
        for room in sorted_rooms:
            room_id = room['id']
            if talk['startTime'] >= room_end_time[room_id]:
                schedule[room_id].append(talk['id'])
                room_end_time[room_id] = talk['endTime']
                assigned = True
                break
        # If no room can accommodate the talk (due to time conflicts), skip this talk.
        if not assigned:
            continue

    # The following post-processing evaluates penalty due to keyword diversity.
    # We divide the conference duration into segments based on all talk boundaries.
    boundaries = set()
    for talk in sorted_talks:
        boundaries.add(talk['startTime'])
        boundaries.add(talk['endTime'])
    boundaries = sorted(boundaries)
    
    # Build a mapping from talk id to talk info for easy lookup.
    talk_dict = {talk['id']: talk for talk in talks}
    
    # Compute effective total attendance (this value is not used for scheduling decisions but can be logged or used for further optimization)
    effective_total_attendance = 0
    # For each time segment, compute concurrent talks and their keyword diversity.
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        duration = end - start
        concurrent_talks = []
        for room_id in schedule:
            # For each talk in each room, check if it is running during the current segment.
            for tid in schedule[room_id]:
                talk = talk_dict[tid]
                if talk['startTime'] <= start and talk['endTime'] >= end:
                    concurrent_talks.append(talk)
        # Get the set of unique keywords
        unique_keywords = set()
        for talk in concurrent_talks:
            unique_keywords.update(talk['keywords'])
        segment_attendance = sum(talk['expectedAttendance'] for talk in concurrent_talks)
        # Apply penalty if keyword diversity is below K
        if len(unique_keywords) < K:
            segment_attendance *= penaltyFactor
        # Weight by segment duration (here, simply add because talks may span multiple segments)
        effective_total_attendance += segment_attendance * duration

    # For demonstration, we print effective total attendance.
    # In a real optimization procedure, one might iteratively adjust the schedule based on this metric.
    # For now, the heuristic schedule is returned.
    # You can uncomment the following line for debugging purposes.
    # print("Effective Total Attendance:", effective_total_attendance)
    
    return schedule

if __name__ == "__main__":
    # Example usage:
    talks = [
        {'id': 1, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 100, 'keywords': ['AI', 'ML']},
        {'id': 2, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 80, 'keywords': ['Data Science', 'Statistics']},
        {'id': 3, 'startTime': 600, 'endTime': 660, 'expectedAttendance': 120, 'keywords': ['AI', 'Robotics']},
        {'id': 4, 'startTime': 600, 'endTime': 660, 'expectedAttendance': 90, 'keywords': ['Cloud', 'Security']},
        {'id': 5, 'startTime': 660, 'endTime': 720, 'expectedAttendance': 70, 'keywords': ['AI', 'Robotics', 'Data Mining']},
        {'id': 6, 'startTime': 700, 'endTime': 760, 'expectedAttendance': 110, 'keywords': ['Big Data', 'Analytics']},
    ]
    rooms = [{'id': 'A'}, {'id': 'B'}]
    conferenceDuration = 720  # e.g., 12 hours in minutes
    K = 4
    penaltyFactor = 0.5

    scheduled = schedule_conference(talks, rooms, conferenceDuration, K, penaltyFactor)
    print("Scheduled Conference:", scheduled)