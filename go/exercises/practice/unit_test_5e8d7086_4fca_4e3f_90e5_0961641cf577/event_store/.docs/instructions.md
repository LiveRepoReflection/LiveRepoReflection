## Project Name

```
distributed-event-sourcing
```

## Question Description

You are tasked with designing and implementing a simplified distributed event sourcing system for a microservices architecture. This system needs to reliably record and distribute events across multiple services to maintain a consistent view of application state.

Imagine you are building an e-commerce platform. You have several microservices, including:

*   `OrderService`: Handles order creation, modification, and cancellation.
*   `InventoryService`: Manages product inventory levels.
*   `PaymentService`: Processes payments for orders.
*   `NotificationService`: Sends notifications to customers about order updates.

Each service emits events to reflect state changes. For example, `OrderService` might emit `OrderCreated`, `OrderUpdated`, and `OrderCancelled` events. `InventoryService` might emit `ProductReserved`, `ProductReleased`, and `StockLevelUpdated` events.

Your goal is to build a central `EventStore` service that:

1.  **Persists Events:** Stores events durably. The order of events is critical and must be preserved. Events must be stored in a total order.
2.  **Distributes Events:** Reliably delivers events to interested subscribers (other microservices).
3.  **Supports Subscriptions:** Allows services to subscribe to specific event types.
4.  **Ensures At-Least-Once Delivery:** Guarantees that each subscriber receives every event at least once, even in the face of failures.
5.  **Maintains Read Consistency:** Should support read consistency (e.g. read your writes) while still being performant.

**Specific Requirements:**

*   **Event Structure:** Events should have the following structure:

```go
type Event struct {
    ID        string    `json:"id"`    // Unique event ID (UUID)
    Type      string    `json:"type"`  // Event type (e.g., "OrderCreated")
    Data      []byte    `json:"data"`  // Event data (JSON-encoded)
    Timestamp time.Time `json:"timestamp"` // Event creation timestamp
}
```

*   **EventStore API:** The `EventStore` service should expose the following API:

```go
type EventStore interface {
    Append(event Event) error             // Appends an event to the store
    Subscribe(eventType string, subscriber Subscriber) error // Subscribes a subscriber to an event type
    GetEvents(eventType string, offset int) ([]Event, error) // Retrieves events of a specific type, starting from an offset
}

type Subscriber interface {
    ProcessEvent(event Event) error // Processes an event
}
```

*   **Concurrency:** The `EventStore` must handle concurrent `Append` and `Subscribe` requests safely.
*   **Persistence:** Events should be persisted to a durable storage medium. For simplicity, you can use an in-memory store, but it should be designed to be easily swappable with a persistent store (e.g., PostgreSQL, Kafka, or a custom file-based store).
*   **At-Least-Once Delivery:** Implement a mechanism to ensure at-least-once delivery to subscribers. Consider using acknowledgements or offsets to track delivery progress. Events should be re-delivered if a subscriber fails to acknowledge receipt.
*   **Ordering Guarantee:** Events should be delivered to subscribers in the same order they were appended to the store.
*   **Scalability:** While not a primary focus of the implementation, consider how your design could be scaled horizontally to handle a high volume of events and subscribers.
*   **Error Handling:** Implement proper error handling and logging.

**Constraints:**

*   The `EventStore` service should be implemented in Go.
*   You can use any external libraries or frameworks you deem necessary, but keep the dependencies to a minimum.
*   Focus on correctness, reliability, and performance.
*   Consider the trade-offs between different implementation approaches.

**Bonus Challenges:**

*   Implement a replay mechanism to allow subscribers to catch up on missed events.
*   Implement a mechanism for handling schema evolution of events.
*   Implement a distributed lock to ensure only one instance of the `EventStore` is actively writing to the persistent store at a time (for a high-availability setup).
*   Implement metrics and monitoring to track the performance and health of the `EventStore`.

This problem requires a solid understanding of distributed systems principles, concurrency, and data persistence. The ideal solution will be well-structured, robust, and efficient. Good luck!
