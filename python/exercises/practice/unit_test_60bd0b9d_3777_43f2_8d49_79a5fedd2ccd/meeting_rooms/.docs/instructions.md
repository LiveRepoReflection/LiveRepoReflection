## Project Name

```
OptimalMeetingScheduler
```

## Question Description

You are tasked with designing an efficient meeting scheduler for a large organization. The organization has `n` employees, each with their own calendars. Each employee's calendar consists of a list of time intervals representing busy slots. Your goal is to find the *minimum* number of meeting rooms required to schedule all meeting requests, ensuring no meetings overlap in the same room.

Specifically, you are given:

*   `employees`: A list of lists, where `employees[i]` is a list of time intervals representing the busy slots for the i-th employee. Each time interval is represented as a tuple `(start_time, end_time)`, where `start_time` and `end_time` are integers representing the start and end time of the busy slot, respectively.  All time intervals are within a single day (0 to 24*60 minutes).
*   `meeting_requests`: A list of tuples `(employee_ids, duration)`, where `employee_ids` is a list of integers representing the IDs of the employees required for the meeting, and `duration` is the duration of the meeting in minutes.  Employee IDs are 0-indexed.

Your task is to write a function `min_meeting_rooms(employees, meeting_requests)` that returns the minimum number of meeting rooms required to schedule all meeting requests without any overlaps in the same room.

**Constraints:**

*   `1 <= n <= 500` (number of employees)
*   `0 <= len(employees[i]) <= 100` (number of busy slots per employee)
*   `0 <= start_time < end_time <= 1440` (valid time intervals within a day)
*   `1 <= len(meeting_requests) <= 500`
*   `1 <= len(employee_ids) <= n` (number of attendees per meeting)
*   `1 <= duration <= 1440` (meeting duration)
*   An employee can be in multiple meetings at the same time.
*   All employee IDs in `meeting_requests` are valid (within the range \[0, n-1]).
*   Meeting requests must be scheduled wholly within the bounds of a single day (0-1440).
*   Minimize the number of meeting rooms used.

**Efficiency Requirements:**

*   Your solution should be optimized for both time and space complexity. Brute-force approaches will likely time out. Consider efficient algorithms and data structures for interval management and conflict detection.

**Example:**

```python
employees = [
    [(60, 120), (300, 360)],  # Employee 0
    [(180, 240)],            # Employee 1
    [(420, 480)],            # Employee 2
]

meeting_requests = [
    ([0, 1], 60),  # Meeting 0: Employees 0 and 1, duration 60 minutes
    ([1, 2], 120), # Meeting 1: Employees 1 and 2, duration 120 minutes
]

result = min_meeting_rooms(employees, meeting_requests)
print(result)  # Output: 2
```

**Explanation of the Example:**

*   Meeting 0 (employees 0 and 1, duration 60) can be scheduled from 0 to 60.
*   Meeting 1 (employees 1 and 2, duration 120) can be scheduled from 240 to 360.

Both meetings can happen concurrently with the other busy slots of the employees involved. Since these two meetings can overlap, they require different meeting rooms. Thus, the minimum meeting rooms required are 2.
