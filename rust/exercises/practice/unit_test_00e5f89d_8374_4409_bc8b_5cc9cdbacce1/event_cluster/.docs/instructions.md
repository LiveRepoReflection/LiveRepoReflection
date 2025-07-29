Okay, here's a challenging Rust coding problem designed with the criteria you specified.

## Project Name:

```
distributed-event-scheduler
```

## Question Description:

You are tasked with designing and implementing a distributed event scheduler.  This scheduler is responsible for reliably executing events at specific times across a cluster of machines.

**Scenario:**

Imagine a microservices architecture where different services need to trigger actions in other services at specific points in time.  Instead of each service managing its own scheduled tasks, a central distributed scheduler is used to ensure consistency and reliability.

**Requirements:**

1.  **Event Definition:** An event consists of:
    *   `id`: A unique identifier for the event (String).
    *   `execution_time`:  A UTC timestamp representing the time the event should be executed (u64 representing Unix timestamp in seconds).
    *   `target_service`: The service that should receive the event payload (String).
    *   `payload`:  Arbitrary data to be sent to the target service (String).

2.  **Scheduling:** The scheduler should accept new events to be scheduled.  Events should be persisted to a durable storage (e.g., a database or distributed key-value store).  The scheduler must guarantee at-least-once execution of each event.

3.  **Distribution & Fault Tolerance:** The scheduler should be able to run as multiple independent nodes in a cluster. If a node fails, another node should be able to take over its responsibilities without losing any events or causing duplicate executions beyond what is permitted by the at-least-once guarantee.

4.  **Execution:** At the `execution_time`, the scheduler should deliver the `payload` to the `target_service`. Assume the existence of a function `send_event(target_service: String, payload: String)` that handles the actual delivery.  This function can be assumed to be idempotent for each event. If `send_event` fails, the scheduler should retry the delivery.

5.  **Time Accuracy:** The scheduler should aim for high time accuracy. Deviations from the `execution_time` should be minimized as much as possible.

6.  **Scalability:** The system should be able to handle a large number of scheduled events (millions) and a high rate of new event submissions.

7.  **Concurrency:** The scheduler should handle concurrent event scheduling and execution efficiently.

8.  **Event Removal:** The scheduler should provide a mechanism to remove scheduled events by their `id`. Removal should happen before the execution time. After the execution time, attempting to remove the event should not have any effect.

**Constraints:**

*   Assume that the system clock across all nodes is reasonably synchronized using NTP or similar. (Clock drift should be within acceptable limits for typical use cases)
*   You can use any appropriate libraries or crates in your solution.  Consider using libraries for database interaction, distributed consensus, and concurrency management.
*   Focus on the core scheduling logic and distribution aspects.  You don't need to implement the `send_event` function or set up a real microservices environment.
*   Assume the `send_event` function may transiently fail and should be retried.

**Optimization Requirements:**

*   Minimize the time spent scanning for events ready to be executed.  Avoid full table scans if possible.
*   Optimize for high throughput when scheduling new events.
*   Consider the trade-offs between consistency and performance in a distributed environment.

**Example:**

A new event with `id="event123"`, `execution_time = 1678886400`, `target_service = "billing-service"`, and `payload = "charge_user_123"` is scheduled. At time 1678886400, the scheduler should call `send_event("billing-service", "charge_user_123")`.

**Deliverables:**

*   Rust code implementing the distributed event scheduler.
*   A brief design document explaining your architecture, data structures, and algorithms.  Address the trade-offs you made and how you met the requirements.
*   Explanation of how the solution satisfies all requirements and constraints.
*   Documentation of all the edge cases you handled, and how your system behaves under failure scenarios (e.g. one or more nodes crash).

This problem requires a deep understanding of distributed systems, concurrency, data structures, and algorithms.  There are multiple valid approaches, each with different trade-offs.  The challenge is to design a robust, scalable, and efficient solution that meets all the requirements and constraints. Good luck!
