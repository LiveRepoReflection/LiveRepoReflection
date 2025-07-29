from collections import defaultdict
import heapq


def find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours):
    """
    Finds the optimal meeting time that minimizes disruption.
    
    Args:
        employees (list): List of employee dictionaries with 'id', 'level', and 'availability'.
        meeting_duration (int): The duration of the meeting in minutes.
        required_attendees (list): List of employee IDs who must attend.
        optional_attendees (list): List of employee IDs who are optional.
        working_hours (tuple): The (start_time, end_time) tuple representing working hours.
    
    Returns:
        tuple: The optimal (start_time, end_time) for the meeting, or None if no valid time is found.
    """
    # Create a mapping of employee IDs to their information
    employee_map = {emp['id']: emp for emp in employees}
    
    # Check if there are any required attendees
    if not required_attendees:
        # If there are no required attendees, we need to find a time that
        # minimizes disruption for all optional attendees
        all_attendees = optional_attendees
    else:
        all_attendees = required_attendees.copy()
        all_attendees.extend([eid for eid in optional_attendees if eid not in all_attendees])
    
    # Get the working hours boundaries
    work_start, work_end = working_hours
    
    # Create a list of all possible time slot boundaries
    time_points = set([work_start, work_end])
    
    # Add all availability boundaries to the time points
    for emp_id in all_attendees:
        employee = employee_map[emp_id]
        for start, end in employee['availability']:
            time_points.add(start)
            time_points.add(end)
    
    # Convert to sorted list
    time_points = sorted(time_points)
    
    # Create a list of all potential meeting start times
    potential_start_times = [t for t in time_points if t + meeting_duration <= work_end]
    
    # If no potential start times, return None
    if not potential_start_times:
        return None
    
    # For each potential start time, calculate the disruption score
    best_time = None
    min_disruption = float('inf')
    
    for start_time in potential_start_times:
        end_time = start_time + meeting_duration
        
        # Skip if the meeting would go beyond working hours
        if end_time > work_end:
            continue
        
        # Check if all required attendees can attend
        required_can_attend = True
        for emp_id in required_attendees:
            can_attend = False
            for avail_start, avail_end in employee_map[emp_id]['availability']:
                if start_time >= avail_start and end_time <= avail_end:
                    can_attend = True
                    break
            if not can_attend:
                required_can_attend = False
                break
        
        # Skip if not all required attendees can attend
        if not required_can_attend:
            continue
        
        # Calculate disruption score
        disruption_score = 0
        for emp in employees:
            emp_id = emp['id']
            # Skip calculating for employees not in the meeting
            if emp_id not in all_attendees:
                continue
                
            can_attend = False
            for avail_start, avail_end in emp['availability']:
                if start_time >= avail_start and end_time <= avail_end:
                    can_attend = True
                    break
            
            if not can_attend:
                disruption_score += emp['level']
        
        # Update the best time if this is better
        if disruption_score < min_disruption:
            min_disruption = disruption_score
            best_time = (start_time, end_time)
    
    return best_time


def find_optimal_meeting_time_optimized(employees, meeting_duration, required_attendees, optional_attendees, working_hours):
    """
    An optimized version of find_optimal_meeting_time.
    This implementation is more efficient for large numbers of employees.
    
    Args:
        employees (list): List of employee dictionaries with 'id', 'level', and 'availability'.
        meeting_duration (int): The duration of the meeting in minutes.
        required_attendees (list): List of employee IDs who must attend.
        optional_attendees (list): List of employee IDs who are optional.
        working_hours (tuple): The (start_time, end_time) tuple representing working hours.
    
    Returns:
        tuple: The optimal (start_time, end_time) for the meeting, or None if no valid time is found.
    """
    # Create a mapping of employee IDs to their information
    employee_map = {emp['id']: emp for emp in employees}
    
    # Get the working hours boundaries
    work_start, work_end = working_hours
    
    # Create mappings for efficient lookup
    required_set = set(required_attendees)
    all_attendees = required_attendees + [emp_id for emp_id in optional_attendees if emp_id not in required_set]
    
    # Process employee availability into discrete time slots
    time_events = []
    
    for emp_id in all_attendees:
        emp = employee_map[emp_id]
        for start, end in emp['availability']:
            # Only consider availability that overlaps with working hours
            adj_start = max(start, work_start)
            adj_end = min(end, work_end)
            
            if adj_start < adj_end and adj_end - adj_start >= meeting_duration:
                # Add availability start and end events to our list
                time_events.append((adj_start, 1, emp_id, emp['level']))  # 1 for start event
                time_events.append((adj_end, -1, emp_id, emp['level']))   # -1 for end event
    
    # Sort by time, then make end events come before start events if times are the same
    time_events.sort(key=lambda x: (x[0], x[1]))
    
    # Scan through the events to find valid meeting times
    available_employees = set()
    potential_meeting_times = []
    
    for i, (time, event_type, emp_id, level) in enumerate(time_events):
        # Update available employees
        if event_type == 1:  # Start of availability
            available_employees.add(emp_id)
        else:  # End of availability
            available_employees.remove(emp_id)
        
        # Check if a valid meeting can start at this time
        if i < len(time_events) - 1:
            next_time = time_events[i+1][0]
            duration = next_time - time
            
            # We need to check if the meeting can start at 'time' and end at 'time + meeting_duration'
            if duration >= meeting_duration and time + meeting_duration <= work_end:
                # Check if all required attendees are available
                if all(emp_id in available_employees for emp_id in required_attendees):
                    # Calculate disruption score
                    disruption = sum(employee_map[emp_id]['level'] 
                                    for emp_id in all_attendees 
                                    if emp_id not in available_employees)
                    
                    heapq.heappush(potential_meeting_times, (disruption, time, time + meeting_duration))
    
    # Return the meeting time with the minimum disruption
    if potential_meeting_times:
        _, start, end = heapq.heappop(potential_meeting_times)
        return (start, end)
    else:
        return None


# Use the optimized version as the primary function
find_optimal_meeting_time = find_optimal_meeting_time_optimized