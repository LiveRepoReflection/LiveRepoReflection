Okay, here's a challenging Go coding problem designed to test advanced data structure knowledge, algorithmic thinking, and attention to edge cases.

**Project Name:** `concurrent-data-structures`

**Question Description:**

You are tasked with implementing a concurrent, lock-free, multi-producer, single-consumer (MPSC) queue in Go.  This queue will be used in a high-throughput system where multiple worker goroutines produce data and a single consumer goroutine processes it.

The queue must meet the following requirements:

1.  **Lock-Free:** The queue implementation *must not* use mutexes or other explicit locking mechanisms.  Atomicity and synchronization should be achieved using atomic operations provided by the `sync/atomic` package.

2.  **MPSC (Multi-Producer, Single-Consumer):**  The queue must be safe for concurrent access from multiple producer goroutines and a single consumer goroutine. The consumer *must* be a single goroutine.

3.  **Bounded Capacity:** The queue must have a fixed capacity, specified during initialization.  Producers should not be able to enqueue elements beyond this capacity.

4.  **Non-Blocking Enqueue/Dequeue:** Producers should be able to attempt to enqueue without blocking. If the queue is full, the enqueue operation should return an error. The consumer should be able to attempt to dequeue without blocking. If the queue is empty, the dequeue operation should return an error.

5.  **Error Handling:**  Provide appropriate error types to indicate queue full and queue empty conditions.

6.  **FIFO (First-In, First-Out):** The queue must maintain the order of elements.

7.  **Memory Safety:** The implementation must be memory-safe and avoid data races.

8.  **Efficiency:** The solution should be as efficient as possible, minimizing contention and maximizing throughput.  Consider padding data structures to avoid false sharing.

9.  **Generic Type:** Implement the queue using generics so that it can hold any type.

**Specific Requirements:**

*   Implement a `Queue[T]` type with the following methods:

    *   `NewQueue[T](capacity int) *Queue[T]`:  Creates a new queue with the specified capacity. Returns `nil` if the capacity is invalid (<= 0).
    *   `Enqueue(item T) error`:  Attempts to enqueue an item. Returns `nil` on success, or an error if the queue is full.
    *   `Dequeue() (T, error)`: Attempts to dequeue an item. Returns the dequeued item and `nil` on success, or the zero value of the type `T` and an error if the queue is empty.
    *   `Len() int`: Returns the current number of elements in the queue.
    *   `Cap() int`: Returns the queue's capacity.

*   Define custom error types `ErrQueueFull` and `ErrQueueEmpty`.

*   You are **forbidden** from using channels, mutexes, or `select` statements in your implementation.  You **must** use atomic operations.

*   Consider using padding to avoid false sharing between the head and tail pointers.

*   Implement a test suite that thoroughly tests the queue's functionality, including concurrent enqueue and dequeue operations, edge cases (empty queue, full queue), and correct error handling. The tests should run with `-race` flag.

This problem requires a deep understanding of concurrent programming, atomic operations, and data structure design. The lock-free constraint significantly increases the complexity. The bounded capacity and non-blocking requirements add further challenges to ensuring correctness and efficiency.
