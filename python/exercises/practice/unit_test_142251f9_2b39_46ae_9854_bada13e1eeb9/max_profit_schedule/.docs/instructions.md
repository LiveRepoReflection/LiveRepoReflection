## Project Name

`MaximumProfitScheduling`

## Question Description

You are given a list of tasks, each with a start time, end time, and a profit associated with completing that task. Your goal is to schedule a subset of these tasks such that the total profit is maximized, with the constraint that no two tasks can overlap in time.

Formally, you are given a list of tuples, `tasks`, where each tuple `(start_time, end_time, profit)` represents a task.  `start_time` and `end_time` are non-negative integers representing the start and end time of the task, respectively. `profit` is a positive integer representing the profit earned by completing the task.

Your task is to write a function that takes the `tasks` list as input and returns the maximum total profit that can be earned by scheduling a non-overlapping subset of tasks.

**Constraints and Considerations:**

*   **Large Input:** The number of tasks can be very large (up to 10<sup>5</sup>). Efficient algorithms are necessary to avoid exceeding time limits.
*   **Integer Overflow:** Be mindful of potential integer overflows when calculating profits, especially when dealing with a large number of tasks and large profit values. Consider using appropriate data types to handle large numbers.
*   **Edge Cases:** Handle cases where the input list is empty or contains invalid task durations (e.g., `start_time > end_time`).
*   **Task Order:** The input tasks are not guaranteed to be sorted by any particular order (start time, end time, or profit).  Your solution should work correctly regardless of the initial task order.
*   **Time Complexity:** Aim for a time complexity significantly better than O(n<sup>2</sup>), where n is the number of tasks. Algorithms like dynamic programming with appropriate optimizations or divide-and-conquer approaches are recommended.
*   **Memory Usage:** Keep memory usage in mind, especially with large input sizes. Avoid storing unnecessary copies of the input data.
*   **Multiple Valid Solutions:** There might be multiple optimal schedules achieving the same maximum profit. Your function only needs to return the maximum profit value, not the specific tasks in the schedule.
*   **Non-Negative Times:** Start and end times are non-negative integers. The difference between end and start times, however, may be large.

**Example:**

```python
tasks = [(1, 2, 50), (3, 5, 20), (6, 19, 100), (2, 100, 200)]
max_profit = solve_maximum_profit_scheduling(tasks)  # Expected output: 250 (tasks (1,2,50) and (6,19,100) and (3,5,20)
 tasks = [(1, 3, 5), (2, 4, 6), (3, 5, 2), (6, 7, 3)]
 max_profit = solve_maximum_profit_scheduling(tasks)  # Expected output: 14 (tasks (2,4,6), (6,7,3), (1,3,5))
```
