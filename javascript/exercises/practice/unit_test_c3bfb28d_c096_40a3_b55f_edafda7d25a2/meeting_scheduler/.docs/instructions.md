## Project Name

`OptimalMeetingScheduler`

## Question Description

You are tasked with building an efficient meeting scheduler for a large organization. The organization has a complex hierarchical structure with various teams and departments. Each employee has a calendar with existing appointments and availability slots.

Your scheduler must be able to handle the following requests:

1.  **Schedule a meeting:** Given a list of employee IDs, a meeting duration, a meeting priority (High, Medium, Low), and a time range within which the meeting must be scheduled, find an optimal time slot for the meeting.

2.  **Reschedule a meeting:** Given a meeting ID, a new list of employee IDs, a new meeting duration, a new meeting priority, and a new time range, find an optimal time slot for the meeting. The original meeting should be cancelled upon successful rescheduling.

3.  **Cancel a meeting:** Given a meeting ID, cancel the meeting and free up the time slots in all the involved employees' calendars.

**Optimality Criteria:**

The scheduler should prioritize the following factors in descending order:

*   **Priority:** High-priority meetings should be scheduled before lower-priority meetings. If two meetings have the same priority, the one requested earlier should be scheduled first.
*   **Employee Rank:** Meetings involving higher-ranking employees should be scheduled earlier. The employee rank is determined by their position in the organizational hierarchy (e.g., CEO > Manager > Employee). You are given a function to determine the rank of any employee ID.
*   **Minimizing Calendar Fragmentation:** The scheduler should minimize the creation of small, isolated free slots in employees' calendars. It should prefer slots that are adjacent to existing meetings or busy times.
*   **Earliest Start Time:** Among equally good slots, the scheduler should choose the earliest possible start time within the given time range.

**Constraints:**

*   The number of employees in the organization can be very large (up to 1 million).
*   The number of meetings to be scheduled per day can be significant (up to 10,000).
*   The time range for scheduling a meeting can be several days.
*   The scheduler should be highly performant and responsive. Minimize latency for all operations.
*   The solution should be memory-efficient.

**Input:**

*   Employee Calendars: A data structure storing the availability of each employee. You must design this data structure.
*   Organizational Hierarchy: A function `getEmployeeRank(employeeId)` that returns the rank of an employee. Higher numbers indicate higher rank.
*   Meeting Requests: Data structures containing the information for each meeting request (employee IDs, duration, priority, time range, meeting ID).

**Output:**

*   Schedule a meeting: Return the start time of the scheduled meeting, or `null` if no suitable slot is found.
*   Reschedule a meeting: Return the new start time of the rescheduled meeting, or `null` if no suitable slot is found.
*   Cancel a meeting: Return `true` if the meeting was successfully cancelled, or `false` if the meeting ID was not found.

**Edge Cases:**

*   Overlapping time ranges for different meetings involving the same employee(s).
*   Meeting duration exceeding the available time slots.
*   No common free time slots for all requested employees within the given time range.
*   Invalid employee IDs in the meeting request.
*   Rescheduling a meeting that does not exist.
*   Handling concurrent requests to schedule, reschedule, and cancel meetings.

**Bonus Challenges:**

*   Implement conflict resolution for concurrent meeting requests.
*   Add support for recurring meetings.
*   Design an API for external systems to access the meeting scheduler.
*   Implement a user interface to visualize the meeting schedules.
