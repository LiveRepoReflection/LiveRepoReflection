Okay, I'm ready to design a challenging programming competition problem. Here's the problem statement:

## Project Name

`Scalable-Event-Scheduler`

## Question Description

You are tasked with designing a scalable event scheduler for a large distributed system. This system needs to handle a massive influx of event scheduling requests and execute them reliably at the specified times.

Each event has the following attributes:

*   `event_id`: A unique string identifier for the event.
*   `execution_time`: A Unix timestamp (in seconds) representing the time at which the event should be executed.
*   `payload`: A string containing the data that needs to be passed to the event handler when the event is executed.
*   `priority`: An integer representing the priority of the event. Higher numbers indicate higher priority.

The system consists of multiple worker nodes that are responsible for executing the scheduled events. Your solution should efficiently distribute the events across these worker nodes, ensuring that events are executed on time and in the correct order of priority.

Your program should implement the following functionality:

1.  **Event Submission**: Implement a function `schedule_event(event_id, execution_time, payload, priority)` that adds a new event to the scheduler. The function should return `True` if the event was successfully scheduled, and `False` otherwise (e.g., if an event with the same `event_id` already exists).

2.  **Event Cancellation**: Implement a function `cancel_event(event_id)` that removes an event from the scheduler. The function should return `True` if the event was successfully cancelled, and `False` otherwise (e.g., if the event does not exist).

3.  **Event Retrieval**: Implement a function `get_next_events(current_time, max_events)` that retrieves a list of up to `max_events` events that are scheduled to execute at or before `current_time`, sorted by priority in descending order (highest priority first) and then by execution time in ascending order (earliest first). The returned events should be removed from the scheduler. The function should return a list of tuples, where each tuple contains the `event_id` and `payload` of the event.

4.  **Scalability and Fault Tolerance**: The system should be designed to handle a large number of events (millions) and a high rate of event submissions and cancellations. It should also be fault-tolerant, meaning that it should be able to continue operating correctly even if some of the worker nodes fail. Assume a simplified failure model where nodes can crash, but data is durable.

5.  **Time Complexity**: The `schedule_event`, `cancel_event`, and `get_next_events` functions should be implemented with optimal time complexity. Excessive processing time will be penalized in grading.

6.  **Memory Usage**: The solution should be memory-efficient. Excessive memory usage will be penalized.

**Constraints:**

*   The number of events can be very large (up to millions).
*   The rate of event submissions and cancellations can be high.
*   The number of worker nodes is variable.
*   Events must be executed on time, with minimal delay.
*   Higher priority events must be executed before lower priority events with the same execution time.
*   The solution must be thread-safe. Multiple threads can access the scheduler concurrently.
*   You can use any standard Python libraries.  External libraries *should* be avoided unless absolutely necessary and clearly justified.

**Grading Criteria:**

*   Correctness: The solution must correctly schedule, cancel, and retrieve events.
*   Performance: The solution must be efficient in terms of time and memory usage.
*   Scalability: The solution must be able to handle a large number of events and a high rate of event submissions and cancellations.
*   Fault Tolerance: The solution must be able to continue operating correctly even if some of the worker nodes fail (simulated through controlled data access restrictions).
*   Code Quality: The code must be well-structured, readable, and maintainable.

This problem requires a good understanding of data structures, algorithms, concurrency, and system design principles. It challenges contestants to think about trade-offs between different design choices and to optimize their solution for performance and scalability. Good luck!
