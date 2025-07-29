## Project Name

```
Distributed Event Stream Processor
```

## Question Description

You are tasked with designing and implementing a distributed system for processing a high-volume stream of events. The system should be able to handle various types of events, perform complex transformations, and route events to different destinations based on configurable rules.

**Scenario:**

Imagine you are building a real-time analytics platform for a large e-commerce website. The website generates a continuous stream of events such as `product_viewed`, `product_added_to_cart`, `order_placed`, `payment_processed`, etc. You need to process this stream to derive insights such as:

*   Real-time sales dashboards
*   Personalized product recommendations
*   Fraud detection

**Requirements:**

1.  **Event Ingestion:** The system must be able to ingest a high volume of events (millions per second). The events are serialized using Protocol Buffers (protobuf).

2.  **Distributed Processing:** The processing should be distributed across multiple nodes to handle the load and provide fault tolerance.

3.  **Configurable Rules:** The system must support configurable routing rules. These rules determine where events are sent based on event attributes. Rules should be dynamically updatable without system downtime. An example rule might be "Send all `order_placed` events with a total value greater than $1000 to the fraud detection system."

4.  **Complex Transformations:** The system should be able to perform complex stateful transformations on the event stream. For example, calculating a 5-minute moving average of sales for each product category.

5.  **Fault Tolerance:** The system should be resilient to node failures. Events should not be lost, and processing should continue without interruption.

6.  **Scalability:** The system should be easily scalable to handle increasing event volumes.

7.  **Latency:** The system should provide low-latency processing. End-to-end latency (from event ingestion to result delivery) should be minimized.

8.  **Ordering Guarantees:** While perfect global ordering is not required, strive to maintain event order within a reasonable time window for each user session.

**Constraints:**

*   You must use Rust for implementing the core components of the system.
*   You can use external libraries and frameworks as needed.  Consider those related to networking, distributed systems, data serialization, and concurrency.
*   The system must be designed to run on commodity hardware (e.g., standard Linux servers).
*   Assume that event schemas are predefined and available as protobuf definitions.

**Deliverables:**

*   A well-documented Rust codebase implementing the core components of the distributed event stream processor.
*   A clear description of the system architecture, including the roles of different components and the data flow.
*   A detailed explanation of the design choices, including the rationale for selecting specific data structures, algorithms, and libraries.
*   A discussion of the trade-offs between different approaches, such as consistency vs. availability, latency vs. throughput.
*   A basic benchmarking and testing strategy.

**Judging Criteria:**

*   Correctness: The system correctly processes events and produces accurate results.
*   Performance: The system can handle high event volumes with low latency.
*   Scalability: The system can be easily scaled to handle increasing load.
*   Fault Tolerance: The system is resilient to node failures.
*   Code Quality: The code is well-structured, readable, and maintainable.
*   Design: The system architecture is well-reasoned and addresses the requirements effectively.
*   Documentation: The documentation is clear, concise, and comprehensive.

This problem requires a deep understanding of distributed systems concepts, data structures, algorithms, and Rust programming. Good luck!
