## Project Name

`Distributed Event Deduplication`

## Question Description

You are building a high-throughput, distributed system for processing events.  Each event is represented as a JSON object with a unique `event_id` field.  Due to the nature of the distributed architecture, events can be ingested multiple times from various sources, leading to duplicates. Your task is to design and implement a system that efficiently deduplicates these events in near real-time.

**Specific Requirements:**

1.  **Event Representation:** Events are JSON objects.  Assume the `event_id` field always exists and is a string of alphanumeric characters (a-z, A-Z, 0-9).  The size of each event can vary significantly, ranging from a few bytes to several kilobytes. Other fields in the JSON object are arbitrary and can be ignored for the purpose of deduplication.

2.  **Scale and Throughput:** The system needs to handle a very high volume of events (millions per second). Assume the system will receive a continuous stream of events from a large number of sources.

3.  **Deduplication Window:** You need to deduplicate events within a rolling time window of `T` seconds. After `T` seconds, the system should "forget" about an event, allowing it to be re-ingested as a new event if it arrives again. The value of `T` will be a configuration parameter, and can be as long as one week.

4.  **Distributed Architecture:**  The solution must be designed to be distributed across multiple nodes to handle the high throughput.  Consider how to partition the data and coordinate deduplication across the nodes.

5.  **Fault Tolerance:** The system should be fault-tolerant. If a node fails, the system should continue to operate without significant data loss or service interruption.

6.  **Memory Efficiency:** Given the scale of the system, memory usage is critical. Aim for a solution that minimizes memory footprint while maintaining high performance.

7.  **Latency:** The deduplication process should introduce minimal latency. Ideally, events should be processed and deduplicated within a few milliseconds.

8.  **API:** Implement the following API:

    *   `ingest_event(event: str) -> bool`:  This function takes a JSON string representing an event as input.  It should return `True` if the event is successfully ingested (i.e., it's not a duplicate within the time window), and `False` if it's a duplicate.

9.  **Concurrency:** Implement thread-safe data structures and logic to support concurrent ingestion and deduplication from multiple sources.

**Constraints:**

*   You are constrained by the available memory on each node. Assume nodes have limited RAM.
*   Network latency between nodes should be considered, and the solution should minimize inter-node communication.
*   You are allowed to use external libraries or frameworks, but justify your choices based on performance and scalability considerations.
*   The system must handle out-of-order events (events that arrive slightly delayed).

**Bonus Challenges:**

*   Implement a mechanism for dynamically adjusting the deduplication window `T` based on system load or other factors.
*   Develop a monitoring system to track the deduplication rate, latency, and resource usage.
*   Implement a data persistence strategy to handle node failures and ensure data durability.

**Evaluation Criteria:**

Your solution will be evaluated based on:

*   Correctness (accurate deduplication).
*   Performance (throughput and latency).
*   Scalability (ability to handle increasing event rates).
*   Memory efficiency.
*   Fault tolerance.
*   Code quality (readability, maintainability, and testability).
*   Design choices and justifications.

This is a challenging problem that requires a deep understanding of distributed systems, data structures, and algorithms. Good luck!
