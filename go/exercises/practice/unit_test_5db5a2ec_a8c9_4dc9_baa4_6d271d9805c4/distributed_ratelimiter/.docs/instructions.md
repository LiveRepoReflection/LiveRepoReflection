## Problem: Distributed Rate Limiter with Weighted Resource Allocation

**Description:**

You are tasked with designing and implementing a distributed rate limiter service. This service is responsible for controlling the rate at which clients can access a set of shared resources. The resources are not identical; each resource has a different "weight" representing its cost or capacity. The rate limiter must ensure that clients do not exceed their allocated "credits" over a sliding time window, considering the weight of each resource they access.

**Specifics:**

1.  **Clients and Resources:** The system manages multiple clients, each identified by a unique string ID. There are also multiple resources, each identified by a unique string ID, and each resource has a weight (a positive integer).

2.  **Credit System:** Each client has a credit limit, representing the maximum total weight of resources they can access within a given time window. This credit limit is a positive integer.

3.  **Sliding Time Window:** The rate limiting is enforced over a sliding time window of a fixed duration, let's say 60 seconds.

4.  **Resource Access:** When a client attempts to access a resource, the rate limiter must check if the client has sufficient credits remaining within the current time window, considering the resource's weight.

5.  **Distributed Architecture:** The rate limiter service is distributed across multiple nodes. You must ensure that the rate limiting is consistent across all nodes, even in the presence of concurrent requests.

6.  **Atomic Operations:** All operations related to credit consumption and checking must be atomic to prevent race conditions.

7.  **Eviction Policy:** Implement an eviction policy to automatically remove inactive clients (clients who haven't made a request within a defined time, e.g., 24 hours) from the rate limiter's data structures to prevent memory exhaustion.

8.  **Persistence (Optional):** Consider the case where rate limiter data needs to be persisted to disk (e.g., using Redis or similar). How would you design the system to handle persistence and recovery? (This part won't be directly tested, but it's a design consideration).

**Functionality Required:**

Implement the following functions:

*   `InitializeRateLimiter(window int, eviction int) RateLimiter`: Initializes the rate limiter with a window duration(seconds) and eviction duration(seconds).
*   `SetClientLimit(clientID string, limit int) error`: Sets the credit limit for a specific client.
*   `SetResourceWeight(resourceID string, weight int) error`: Sets the weight for a specific resource.
*   `Allow(clientID string, resourceID string) (bool, error)`: Checks if the client is allowed to access the resource, considering the remaining credits and the resource weight. If allowed, the client's credits should be reduced by the resource weight. If not allowed, return `false` and do not modify the client's credits.
*   `ResetClient(clientID string)`: Resets the credit usage for a specific client (effectively setting their used credits to zero).

**Constraints:**

*   **Concurrency:** The solution must be thread-safe and handle concurrent requests efficiently.
*   **Efficiency:** The `Allow` function should have a time complexity of O(log n) or better, where n is the number of requests within the time window for a specific client.
*   **Scalability:** The design should be scalable to handle a large number of clients and resources.
*   **Accuracy:** Rate limiting should be accurate; clients shouldn't be able to significantly exceed their credit limits.
*   **Error Handling:** The code should handle invalid inputs and potential errors gracefully.
*   **Eviction:** Inactive clients should be evicted automatically and efficiently.

**Edge Cases to Consider:**

*   Non-existent client.
*   Non-existent resource.
*   Setting negative or zero credit limits or resource weights.
*   Concurrent requests for the same client and resource from different nodes.
*   System clock skew across different nodes.
*   Handling very large numbers of clients and resources.
*   Eviction running concurrently with other operations.

This problem requires careful consideration of data structures, algorithms, concurrency, and system design principles. A naive solution will likely fail to meet the performance or scalability requirements.
