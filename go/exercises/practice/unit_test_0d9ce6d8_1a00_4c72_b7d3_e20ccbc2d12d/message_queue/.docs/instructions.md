## Project Name

`ScalableMessageQueue`

## Question Description

You are tasked with designing and implementing a simplified, in-memory message queue system in Go. This system needs to handle a high volume of messages and a large number of concurrent producers and consumers.

The core functionalities of the message queue are:

1.  **Publishing Messages:** Producers can publish messages to a specific topic. Messages are simple strings.
2.  **Subscribing to Topics:** Consumers can subscribe to one or more topics.
3.  **Receiving Messages:** Consumers receive messages published to the topics they are subscribed to, in the order they were published.
4.  **Message Persistence (Limited):** The queue should hold a fixed number of recent messages per topic. Older messages are discarded using a First-In-First-Out (FIFO) approach.
5.  **Concurrency:** The system must handle concurrent publishing and consuming efficiently.
6.  **Ordering Guarantee:** Messages published to a topic should be delivered to each subscriber in the order they were published.

**Specific Requirements and Constraints:**

*   **In-Memory:** The message queue must operate entirely in memory. No external database or file system persistence is required.
*   **Topics:** The message queue should support an arbitrary number of topics. Topic names are strings.
*   **Scalability:** The design should be scalable to handle a large number of concurrent producers and consumers.  Consider how you'll handle locking/synchronization. Avoid global locks.
*   **Message Retention:** Each topic should have a configurable message retention limit (e.g., the last 1000 messages). If a consumer falls behind or reconnects, it will only receive messages within this retention window.  When the retention limit is exceeded, the oldest messages should be removed.
*   **Consumer Groups (Optional):** You do *not* need to implement consumer groups.  Each subscriber receives *all* messages for the topics they subscribe to.
*   **Error Handling:** Implement basic error handling for invalid operations (e.g., subscribing to a non-existent topic).
*   **Efficiency:** Strive for efficient message publishing and delivery. Consider the data structures used and the potential for bottlenecks.
*   **No external message queue libraries (e.g., Kafka, RabbitMQ) allowed.** The goal is to implement a simplified version from scratch.
*   **Bounded Memory Usage:** Be mindful of memory usage.  Ensure that the system does not consume excessive memory, especially with a large number of topics and messages.  Consider using techniques to limit memory growth.
*   **Topic Auto-Creation:** If a message is published to a topic that does not exist, the topic should be automatically created.

**Your Task:**

Implement the core components of the message queue system, including:

1.  A `MessageQueue` struct that manages topics and messages.
2.  Methods for publishing messages to a topic (`Publish`).
3.  Methods for subscribing to topics (`Subscribe`).
4.  A mechanism for consumers to receive messages from the topics they are subscribed to (`Consume`). This mechanism should ideally be non-blocking and allow consumers to asynchronously receive messages.

**Bonus Challenges:**

*   Implement a mechanism to dynamically adjust the message retention limit for each topic.
*   Implement metrics collection (e.g., number of messages published, number of consumers, message latency).

This problem requires a solid understanding of concurrency, data structures, and system design principles. It emphasizes efficient and scalable implementation in Go. Good luck!
