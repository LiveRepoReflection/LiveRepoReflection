## Project Name

`DistributedCacheInvalidation`

## Question Description

You are designing a distributed caching system for a social media platform. This system needs to cache frequently accessed social media posts to reduce latency and database load. However, social media posts can be updated frequently, and these updates need to be reflected in the cache quickly to avoid serving stale data to users.

Your task is to implement a cache invalidation mechanism that ensures data consistency across multiple cache nodes in a distributed environment.

**Specific Requirements:**

1.  **Cache Architecture:** Assume a distributed cache with `N` cache nodes. Each node can independently cache posts. You are given a `CacheNode` struct with basic `get` and `set` methods (provided in the starter code – do *not* implement this).
2.  **Eventual Consistency:** Aim for eventual consistency. It's acceptable for a brief period of time to serve stale data from some cache nodes, but the system should converge to a consistent state relatively quickly.
3.  **Invalidation Propagation:** Implement a mechanism to propagate invalidation messages to all cache nodes when a post is updated.
4.  **Invalidation Strategies:** Implement two cache invalidation strategies:
    *   **Write-Through:** Updates to the database are immediately propagated to the cache *before* the database write is considered complete. This offers strong consistency but potentially increases write latency.
    *   **Write-Invalidate:** Updates are written to the database first.  Then, invalidation messages are sent to the cache nodes, instructing them to remove the stale entry. This offers lower write latency but requires careful handling of race conditions.
5.  **Concurrency:** The system should be able to handle concurrent updates to the same post.
6.  **Scalability:**  Consider the scalability of your solution.  How would your design perform with thousands of cache nodes and a high volume of updates?
7.  **Fault Tolerance:**  The system should be reasonably fault-tolerant.  Consider what happens if one or more cache nodes fail to receive an invalidation message.
8. **Optimization:** Optimize for both read latency (how quickly data can be retrieved from the cache) and write latency (how quickly updates can be applied).  Different strategies will offer different trade-offs.

**Constraints:**

*   `N` (number of cache nodes) will be between 1 and 1000.
*   The cache nodes communicate via a reliable message queue (you don't need to implement the message queue, assume it exists and delivers messages in order eventually).
*   Post IDs are integers.
*   Post content is a string.
*   Assume the database update operation is atomic.
*   The system must handle a high rate of concurrent reads and writes.
*   Minimize unnecessary communication between cache nodes.
*   The system should be resilient to temporary network partitions or node failures.

**Implement the following functions:**

*   `UpdatePost(postID int, content string, strategy string)`: Updates a post in the database and propagates the invalidation message to the cache nodes based on the specified strategy ("write-through" or "write-invalidate").
*   `GetPost(postID int)`: Retrieves a post from the cache. If the post is not in the cache, it should retrieve it from the database, cache it, and return it.

**Bonus:**

*   Implement a "time-to-live" (TTL) mechanism for cached posts to automatically expire stale data.
*   Implement a mechanism to detect and resolve inconsistencies between cache nodes.
*   Implement a monitoring system to track cache hit rate, invalidation latency, and overall system performance.

This problem requires a strong understanding of distributed systems concepts, concurrency, caching strategies, and fault tolerance. Good luck!
