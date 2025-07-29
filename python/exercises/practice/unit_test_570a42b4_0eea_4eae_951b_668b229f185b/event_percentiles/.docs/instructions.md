## Problem: Scalable Event Stream Aggregation

You are building a real-time analytics platform that processes a continuous stream of events. Each event has a timestamp (Unix epoch in seconds), a user ID (integer), and a numerical value (float). The platform needs to efficiently aggregate these events over sliding time windows and compute percentiles of the event values within each window.

**Specific Requirements:**

1.  **Sliding Window Aggregation:** Implement a system that maintains aggregations of events over multiple, concurrent, sliding time windows. You will be given a list of window sizes (in seconds) at initialization. For example, `[60, 300, 3600]` represents windows of 1 minute, 5 minutes, and 1 hour.
2.  **Percentile Calculation:** For each window, calculate the specified percentile(s) of the event values *within* that window. You will be given a list of percentiles to calculate (as floats between 0.0 and 1.0, inclusive). For example, `[0.5, 0.95]` represents the 50th (median) and 95th percentiles.
3.  **Real-Time Performance:** The system must handle a high volume of incoming events with low latency. The `process_event` method should be as efficient as possible.
4.  **Memory Efficiency:** The system should be mindful of memory usage, especially when dealing with large event volumes and long time windows. Storing every event value for the entire duration of all windows is not feasible.
5.  **Thread Safety:** The system must be thread-safe, allowing multiple threads to concurrently call the `process_event` and `get_percentiles` methods.
6.  **Approximate Percentiles:** Due to memory constraints and the need for real-time performance, you are allowed to compute *approximate* percentiles. The accuracy of the approximation should be configurable (e.g., using a parameter that controls the size of a data structure used for percentile estimation).  Explain the trade-off between accuracy and memory usage/performance in your solution.
7.  **Timestamp Ordering:** Events may not arrive in strict timestamp order. The system must handle out-of-order events correctly.  However, you can assume that the timestamps will be within a reasonable bound (e.g., within a few minutes) of the current time. Events that are significantly older than the current time can be discarded.

**Methods to Implement:**

*   `__init__(self, window_sizes: List[int], percentiles: List[float], accuracy: float, max_event_age: int)`: Initializes the system.
    *   `window_sizes`: A list of window sizes in seconds (e.g., `[60, 300, 3600]`).
    *   `percentiles`: A list of percentiles to calculate (e.g., `[0.5, 0.95]`).
    *   `accuracy`: A float representing the desired accuracy of the percentile estimation (e.g., `0.01` means within 1%). This parameter will directly influence the memory usage and performance.
    *   `max_event_age`: Maximum age (in seconds) of an event to consider.  Events older than this will be discarded.

*   `process_event(self, timestamp: int, user_id: int, value: float)`: Processes a single event.
    *   `timestamp`: The Unix epoch timestamp of the event (in seconds).
    *   `user_id`: The ID of the user who generated the event.
    *   `value`: The numerical value of the event.

*   `get_percentiles(self, timestamp: int) -> Dict[int, Dict[float, float]]`: Returns the calculated percentiles for each window.
    *   `timestamp`: The current Unix epoch timestamp (in seconds).  This is used to determine the events that fall within each window.
    *   Returns a dictionary where the keys are the window sizes (integers from the `window_sizes` list), and the values are dictionaries mapping percentiles (floats from the `percentiles` list) to their estimated values (floats).

    ```python
    {
        60: {0.5: 10.2, 0.95: 25.7},  # Percentiles for the 60-second window
        300: {0.5: 9.8, 0.95: 24.1}, # Percentiles for the 300-second window
        3600: {0.5: 11.5, 0.95: 26.3} # Percentiles for the 3600-second window
    }
    ```

**Constraints:**

*   Assume timestamps are non-negative integers.
*   User IDs are positive integers.
*   Event values are floats.
*   The number of window sizes and percentiles will be relatively small (e.g., less than 10).
*   The event stream can be very large (millions or billions of events).
*   Maximize throughput and minimize latency.

**Bonus:**

*   Implement a mechanism to persist the aggregation state to disk and restore it on restart.
*   Implement a visualization or reporting interface to display the calculated percentiles in real-time.
*   Compare different percentile estimation algorithms (e.g., t-digest, DDSketch) and analyze their performance and accuracy trade-offs in this specific use case.
