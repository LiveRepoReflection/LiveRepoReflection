## Question Title: Distributed Transaction Ordering in a Microservice Architecture

### Question Description:

You are tasked with designing and implementing a robust and scalable system for ordering events representing distributed transactions across a set of microservices.  Imagine a system where multiple microservices (e.g., `OrderService`, `PaymentService`, `InventoryService`) participate in transactions.  Each microservice emits events as it processes its part of a transaction.  These events need to be ordered consistently, even when they originate from different services and are processed asynchronously.

Specifically, you are given a stream of transaction events from various microservices. Each event contains the following information:

*   `transaction_id`: A unique identifier for the overall transaction.
*   `service_id`: An identifier for the microservice that emitted the event.
*   `event_id`: A unique identifier for the event within that microservice's context.
*   `timestamp`: A timestamp representing when the event occurred (using nanoseconds).
*   `payload`: The data associated with the event (can be ignored for ordering purposes).

Your goal is to design and implement an algorithm that takes this stream of unordered events as input and produces a totally ordered stream of events for each `transaction_id`. The order **must** respect the following rules:

1.  **Causality:**  If two events within the same `service_id` have `event_id`s that are sequentially incrementing (e.g., `event_id=5` followed by `event_id=6`), they **must** be ordered according to their `event_id`. The `event_id` represents a local sequence within the service.

2.  **Timestamp Precedence:** If two events from *different* `service_id`s have the same `transaction_id`, the event with the earlier `timestamp` should come first. If timestamps are equal, prioritize smaller `service_id` alphabetically.

3.  **Transaction Completeness:** The ordered stream for each `transaction_id` should contain *all* events related to that transaction before any subsequent processing occurs.

4.  **Scalability:** The system should be able to handle a high volume of events and a large number of concurrent transactions.

5.  **Fault Tolerance:** The system should be designed to handle out-of-order arrival of events (within reasonable bounds, specified below).

**Input:**

A stream of events represented as a vector of tuples. Each tuple has the following structure: `(transaction_id: String, service_id: String, event_id: u64, timestamp: u64, payload: String)`.

**Output:**

A `HashMap<String, Vec<(String, String, u64, u64, String)>>`. The keys of the HashMap are `transaction_id`s. The values are vectors of ordered events for each `transaction_id`, represented as tuples of the same structure as the input.

**Constraints:**

*   The number of unique `transaction_id`s can be large (up to 1,000,000).
*   The number of events per `transaction_id` can vary, but is expected to be in the range of 10-100.
*   The total number of events in the input stream can be very large (up to 100,000,000).
*   Timestamps are represented in nanoseconds.
*   Events for a given `transaction_id` may arrive out-of-order. However, the maximum timestamp skew (difference between the earliest and latest event timestamp for a single transaction) will not exceed 1 second (1,000,000,000 nanoseconds).
*   The `event_id` sequence for each service will be contiguous (no gaps). However, the first event might not start at `event_id = 1`.
*   Memory usage is a significant concern. Aim for a solution that minimizes memory footprint.
*   The code should be written in idiomatic Rust, with considerations for performance and error handling.

**Bonus Challenges:**

*   Implement a mechanism to detect and handle transactions that are incomplete after a reasonable timeout period.
*   Explore different data structures and algorithms to optimize performance under varying workload conditions.
*   Consider how to persist the ordered event streams to durable storage.
