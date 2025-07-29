## Project Name

```
decentralized-social-network
```

## Question Description

You are tasked with designing a core component of a decentralized social network. In this network, users post content that is distributed across multiple nodes. The primary challenge is to efficiently retrieve posts relevant to a specific user, considering the distributed nature of the data and the need for strong consistency guarantees.

Each user has a unique ID (an integer). Posts are represented as tuples: `(post_id, user_id, timestamp, content)`.

The network consists of `N` nodes. Each node maintains a partial, potentially overlapping, copy of the posts. Your system must handle two primary operations:

1.  **Post Creation:** When a user creates a post, it must be reliably propagated to a sufficient number of nodes to ensure its availability and durability. The system must guarantee that the post will eventually be visible to all users who follow the poster, even if some nodes are temporarily unavailable.

2.  **Timeline Retrieval:** Given a user ID and a time range (start\_time, end\_time), retrieve all posts from users that the given user *follows* within that time range. The timeline must be sorted by timestamp in descending order (newest first). To implement that, you are given the follower graph of the social network.

**Specific Requirements:**

*   **Data Distribution:** Posts are distributed across `N` nodes. The distribution strategy is not fixed and can be chosen by you, but it must ensure reasonable redundancy and availability.
*   **Consistency:** Implement a mechanism to maintain consistency across the nodes. You need to ensure that even if some nodes are temporarily offline, the system can still retrieve a consistent view of the timeline. The network is eventually consistent.
*   **Efficiency:** Timeline retrieval should be reasonably efficient, even with a large number of posts and followers. Consider optimizing for both time and space complexity.
*   **Fault Tolerance:** The system should be resilient to node failures. If some nodes are unavailable, the system should still be able to retrieve timelines, possibly with some delay due to eventual consistency.
*   **Scalability:** The system should be designed to scale to a large number of users and posts.
*   **Follower Graph:** The follower graph is represented as a dictionary where keys are user IDs, and values are sets of user IDs that the key user follows. I.e. `follower_graph = {user_id: set(followed_user_ids)}`
*   **Time Range:** The time range is inclusive for both start and end times.

**Constraints:**

*   `N` (number of nodes): 1 <= N <= 100
*   Number of users: Up to 10<sup>6</sup>
*   Number of posts: Up to 10<sup>7</sup>
*   `post_id`, `user_id`, `timestamp` are all integers.
*   Content is a string of at most 256 characters.
*   Timestamps are Unix timestamps (seconds since epoch).
*   Assume nodes can fail and recover.
*   The system must be able to handle concurrent post creations and timeline retrievals.

**Your Task:**

Design and implement the data structures and algorithms necessary to support post creation and timeline retrieval in this decentralized social network, considering the above requirements and constraints. You only need to describe the essential components and core logic. Do not focus on the networking aspects or low-level details of inter-node communication. Concentrate on the data management, consistency, and query optimization aspects.
