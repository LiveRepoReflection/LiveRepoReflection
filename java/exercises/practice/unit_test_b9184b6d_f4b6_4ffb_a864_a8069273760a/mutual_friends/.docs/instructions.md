## Project Name

```
DistributedGraphAnalytics
```

## Question Description

You are tasked with designing and implementing a distributed system for performing graph analytics on a massive graph represented as an adjacency list. The graph represents a social network, where nodes are users and edges represent friendships. The graph is too large to fit into the memory of a single machine and must be distributed across multiple machines.

Your system should support the following query:

**`get_mutual_friends(user_id, k)`**: Find the `k` users who have the most mutual friends with the given `user_id`. If multiple users have the same number of mutual friends, return them in ascending order of `user_id`.

**Constraints and Requirements:**

1.  **Distributed Data:** The graph data (adjacency list) is distributed across `N` machines. Each machine stores a subset of the nodes and their corresponding adjacency lists. You don't control how the graph is initially distributed. Assume the data is already partitioned.
2.  **Massive Graph:** The graph is extremely large, potentially containing billions of nodes and edges.
3.  **Real-time Query Response:** The `get_mutual_friends` query should return results within a reasonable time frame (e.g., seconds).
4.  **Fault Tolerance:** The system should be fault-tolerant. If one or more machines fail, the system should still be able to answer queries, potentially with slightly degraded performance.
5.  **Scalability:** The system should be scalable. It should be able to handle increasing graph sizes and query loads by adding more machines.
6.  **Memory Constraints:** Each machine has limited memory. You cannot load the entire graph into the memory of a single machine.
7.  **Communication Overhead:** Minimize communication between machines to improve performance.
8.  **Data Partitioning Assumption:** You can assume the graph partitioning strategy distributes the nodes such that nodes with high degree are spread across different machines to avoid hotspots. However, you cannot make assumptions about how the graph is partitioned in terms of community structure. The partitioning strategy is unknown.
9.  **External Libraries:** You can use standard Java libraries and data structures. However, you are encouraged to design custom data structures and algorithms to optimize performance. You can assume you do not have access to Spark, Flink, or other large scale data processing frameworks for this problem.
10. **User IDs:** User IDs are integers.
11. **k Value:** The value of `k` will always be a positive integer, and is guaranteed to be smaller or equal to the number of users in the graph.
12. **Adjacency List Format:** Each machine stores its part of the adjacency list in a `Map<Integer, List<Integer>>` where the key is the user ID and the value is a list of their friends' user IDs.
13. **No Duplicate Friendships:** You can assume the adjacency list does not contain duplicate friendships. Each friendship appears only once for a given user.

**Your Task:**

1.  **Design:** Describe the architecture of your distributed system. Explain how the graph data is stored and processed across multiple machines. Specify the data structures and algorithms you will use. Detail the communication protocols between machines. Explain how you handle fault tolerance and scalability.
2.  **Implementation:** Implement the `get_mutual_friends(user_id, k)` function. This function should be callable from any machine in the cluster.
3.  **Optimization:** Identify potential bottlenecks in your design and implementation. Suggest optimization strategies to improve performance. Consider trade-offs between memory usage, communication overhead, and query latency.

This problem requires a good understanding of distributed systems principles, graph algorithms, and data structures. It challenges you to design a system that is efficient, scalable, and fault-tolerant. Good luck!
