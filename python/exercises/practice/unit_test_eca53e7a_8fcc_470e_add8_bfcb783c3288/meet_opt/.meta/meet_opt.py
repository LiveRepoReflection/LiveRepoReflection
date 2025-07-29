from datetime import datetime, timedelta
import pytz

def schedule_meeting(employee_data, department_data, meeting_duration, time_window, priority_attendees=None):
    if priority_attendees is None:
        priority_attendees = []
    # Parse global time window in UTC
    global_start = datetime.fromisoformat(time_window[0]).astimezone(pytz.UTC)
    global_end = datetime.fromisoformat(time_window[1]).astimezone(pytz.UTC)
    meeting_delta = timedelta(minutes=meeting_duration)

    # Prepare department lookup for required attendees
    dept_requirements = {}
    for dept in department_data:
        dept_requirements[dept["department_id"]] = dept["required_attendees"]

    # For each employee, compute availability intervals in UTC clipped to global time window.
    employee_intervals = {}
    candidate_times = set()
    for emp in employee_data:
        emp_id = emp["employee_id"]
        tz = pytz.timezone(emp["timezone"])
        intervals = []
        for avail in emp["availability"]:
            start_local = datetime.fromisoformat(avail[0])
            end_local = datetime.fromisoformat(avail[1])
            # Ensure the datetimes are localized if not already
            if start_local.tzinfo is None:
                start_local = tz.localize(start_local)
            if end_local.tzinfo is None:
                end_local = tz.localize(end_local)
            # Convert to UTC
            start_utc = start_local.astimezone(pytz.UTC)
            end_utc = end_local.astimezone(pytz.UTC)
            # Clip intervals with global time window
            clipped_start = max(start_utc, global_start)
            clipped_end = min(end_utc, global_end)
            if clipped_end - clipped_start >= meeting_delta:
                intervals.append((clipped_start, clipped_end))
                # Add candidate times: the start of the clipped intervals and end - meeting_duration
                candidate_times.add(clipped_start)
                candidate_times.add(clipped_end - meeting_delta)
        employee_intervals[emp_id] = {
            "department_id": emp["department_id"],
            "intervals": intervals
        }
    
    # Remove candidate times that are out of global window
    valid_candidates = []
    for t in candidate_times:
        if global_start <= t and (t + meeting_delta) <= global_end:
            valid_candidates.append(t)
    if not valid_candidates:
        return []
    valid_candidates = sorted(valid_candidates)

    best_candidate = None
    best_cost = None
    best_selection = None

    # For each candidate meeting start time, check which employees are available
    for candidate in valid_candidates:
        meeting_start = candidate
        meeting_end = candidate + meeting_delta
        # Build availability by department mapping for this candidate
        dept_available = {}
        for dept_id in dept_requirements:
            dept_available[dept_id] = []
        for emp_id, info in employee_intervals.items():
            # Check if the employee is available for the entire meeting interval in one of his intervals
            available = False
            for (avail_start, avail_end) in info["intervals"]:
                if avail_start <= meeting_start and avail_end >= meeting_end:
                    available = True
                    break
            if available:
                dept_available[info["department_id"]].append(emp_id)

        valid_candidate = True
        selection = {}
        total_cost = 0
        # For each department, check if requirement can be met
        for dept_id, required in dept_requirements.items():
            available_emp = sorted(dept_available[dept_id])
            if len(available_emp) < required:
                valid_candidate = False
                break
            # Separate available employees into priority and non-priority
            available_priority = [emp for emp in available_emp if emp in priority_attendees]
            available_non_priority = [emp for emp in available_emp if emp not in priority_attendees]
            # Include all available priorities (as per requirement "include all if possible")
            chosen = list(available_priority)
            # If chosen already meets requirement, we select only them.
            if len(chosen) < required:
                # Need to select additional employees from non-priority ones in ascending order
                additional_needed = required - len(chosen)
                if len(available_non_priority) < additional_needed:
                    valid_candidate = False
                    break
                chosen.extend(available_non_priority[:additional_needed])
            # To minimize total cost, we choose minimal set = required number if more than available priorities.
            # But since we must include priority if available, chosen can be more than required.
            selection[dept_id] = sorted(chosen)
            total_cost += len(selection[dept_id])
        if not valid_candidate:
            continue
        # Optimization: minimize total number of employees
        if best_cost is None or total_cost < best_cost or (total_cost == best_cost and meeting_start < best_candidate):
            best_candidate = meeting_start
            best_cost = total_cost
            best_selection = selection

    if best_candidate is None:
        return []
    
    # Union the chosen employee ids from each department and sort them in ascending order
    final_set = set()
    for dept_list in best_selection.values():
        final_set.update(dept_list)
    final_result = sorted(final_set)
    return final_result