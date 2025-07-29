## Problem Title: Scalable Event Correlation Engine

### Problem Description:

You are tasked with designing and implementing a scalable event correlation engine. This engine will receive a continuous stream of events from various sources (e.g., network devices, application servers, security systems). Your goal is to identify specific patterns of events occurring within a defined time window and trigger corresponding alerts.

**Detailed Requirements:**

1.  **Event Ingestion:** The engine must be able to ingest a high volume of events concurrently. Each event is a JSON object containing a timestamp (in milliseconds since epoch), a source identifier (string), and a set of key-value pairs representing event attributes.

    ```json
    {
        "timestamp": 1678886400000,
        "source": "server1",
        "attributes": {
            "event_type": "login_success",
            "user": "john.doe",
            "ip_address": "192.168.1.100"
        }
    }
    ```

2.  **Pattern Definition:** The system must support defining correlation patterns using a simple Domain Specific Language (DSL). A pattern consists of a sequence of event conditions that must be satisfied within a specific time window. Each condition specifies constraints on the event source, event type (a key in the `attributes` dictionary), and attribute values. The comparison of attribute values must support equality, inequality, greater than, less than, and regular expression matching. You can assume that the DSL is already parsed and available as a nested dictionary data structure.

    Example DSL (Python dictionary):

    ```python
    pattern = {
        "name": "SuspiciousLogin",
        "time_window": 60000,  # milliseconds
        "events": [
            {
                "source": ".*", # Regular Expression Matching
                "attributes": {
                    "event_type": "login_failed",
                    "user": "john.doe"
                }
            },
            {
                "source": ".*", # Regular Expression Matching
                "attributes": {
                    "event_type": "login_success",
                    "user": "john.doe"
                }
            }
        ]
    }
    ```
    This pattern detects if a user named john.doe has a login failed event followed by a login success event in 60 seconds.

3.  **Correlation Logic:**  The engine must efficiently correlate incoming events against the defined patterns. When a pattern is matched, the engine should generate an alert containing the pattern name and the list of events that triggered the alert.

4.  **Scalability and Optimization:** The engine must be able to handle a large number of concurrent patterns and a high event throughput. Optimize for memory usage and processing speed. Consider the potential bottlenecks and design accordingly.

5.  **Concurrency:** The event ingestion and correlation processes must be thread-safe and handle concurrent access gracefully. Avoid race conditions and ensure data consistency.

6.  **Time Handling:** Handle potentially out-of-order events. Events can arrive slightly out of timestamp order due to network latency or clock skew. Design the system to tolerate a small degree of timestamp imprecision (e.g., within 1 second).

7. **Resiliency:** The service should be designed to be resilient. If an error occurs during event processing, the service should continue to operate without interruption.

**Constraints:**

*   The solution must be implemented in Python.
*   Use appropriate data structures and algorithms for optimal performance.
*   Consider using libraries like `threading`, `multiprocessing`, `collections.deque`, `heapq`, and regular expression library (`re`).
*   The engine must be able to handle a large number of concurrent patterns (e.g., thousands).
*   The engine must be able to handle a high event throughput (e.g., millions of events per second).
*   Assume the DSL parsing is already handled, and the pattern definitions are provided as nested dictionaries.
*   Assume a single machine solution.

**Deliverables:**

*   Python code implementing the event correlation engine.
*   A brief design document outlining the architecture, data structures used, and optimization strategies.
*   Explain the time and space complexity of your solution.
*   Discuss the trade-offs made in your design.

**Judging Criteria:**

*   Correctness: The engine accurately identifies event patterns and generates alerts.
*   Performance: The engine can handle a high event throughput with low latency.
*   Scalability: The engine can handle a large number of concurrent patterns without significant performance degradation.
*   Code Quality: The code is well-structured, readable, and maintainable.
*   Design: The design is well-thought-out and addresses the scalability and concurrency challenges.
*   Resiliency: The engine gracefully handles errors and continues to operate without interruption.

This problem requires a solid understanding of data structures, algorithms, concurrency, and system design principles. Good luck!
