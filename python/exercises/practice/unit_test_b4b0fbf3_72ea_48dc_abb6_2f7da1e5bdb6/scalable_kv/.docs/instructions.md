## Problem: Scalable Key-Value Store with Range Queries

You are tasked with designing and implementing a highly scalable and efficient key-value store that supports both point lookups and range queries.  This store will be used to manage a massive dataset of sensor readings, where each sensor reading is associated with a timestamp (the key).

**Data Model:**

*   Keys: 64-bit unsigned integers representing timestamps (nanoseconds since epoch).
*   Values: Arbitrary byte arrays (up to 1KB in size).

**Requirements:**

1.  **Scalability:** The system must be able to handle an extremely high volume of read and write requests (millions per second) and scale horizontally across multiple machines.
2.  **Durability:** All writes must be durable. Data loss is unacceptable.
3.  **Availability:** The system should be highly available.  A single machine failure should not impact the ability to read or write data.
4.  **Point Lookups:**  Given a timestamp (key), efficiently retrieve the corresponding value.  Latency should be minimized.
5.  **Range Queries:** Given a start timestamp and an end timestamp, efficiently retrieve all key-value pairs where the key falls within the specified range (inclusive).  The number of results in a range query can vary from zero to millions.
6.  **Data Locality:** Optimize for the scenario where timestamps are generally inserted in increasing order (but not strictly – some out-of-order insertions are possible). Similarly, range queries are often performed on recent data.
7.  **Consistency:**  Reads should provide "read your writes" consistency within a single client session.  Writes are acknowledged upon successful durable storage.
8.  **Memory Efficiency:** Minimize memory footprint per node, especially when dealing with large datasets.

**Constraints:**

*   You are free to choose any appropriate data structures and algorithms in Python.
*   Assume a distributed environment where data is partitioned and replicated across multiple nodes.  You do **not** need to implement the actual networking or distributed consensus protocols. You only need to describe the data structures and algorithms within a single node (including how data is stored and retrieved efficiently).  Focus on the data storage and retrieval aspects.
*   You *must* address how data is partitioned and replicated (at a high level - consistent hashing, etc).
*   You must consider the trade-offs between read and write performance, memory usage, and query efficiency.
*   Explain how you handle out-of-order insertions and data locality optimization.
*   Explain how you ensure data durability and availability.
*   Explain how you would approach optimizing the solution further if you had access to specific hardware features (e.g., persistent memory, fast network interconnects).

**Deliverables:**

1.  A Python-like description of the data structures and algorithms you would use to implement the key-value store on a single node. This should be detailed enough to convey the implementation strategy clearly.  You can use pseudocode or simplified Python constructs.
2.  A high-level overview of the system architecture, including data partitioning and replication strategies.
3.  A discussion of the design choices you made, including the trade-offs considered and the rationale behind your decisions.
4.  A discussion of how the system meets the scalability, durability, availability, consistency, and efficiency requirements.
5.  A discussion of potential optimizations.
