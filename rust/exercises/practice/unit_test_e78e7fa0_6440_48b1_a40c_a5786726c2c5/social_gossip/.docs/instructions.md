## Project Name

```
decentralized-social-network
```

## Question Description

You are tasked with building the core functionality for a decentralized social network. This network uses a peer-to-peer (P2P) architecture, where each user node stores a portion of the network's data. Specifically, each node maintains a set of connections to other nodes (its "friends") and stores a limited-size cache of posts from its friends and friends-of-friends (up to a certain "degree").

Your goal is to implement the following functionalities:

1.  **Node Creation:** A new node can be created with a unique ID.
2.  **Friend Connection:** A node can establish a connection with another node, adding them to its friend list.
3.  **Post Creation:** A node can create a new post, which needs to be propagated through the network.
4.  **Post Retrieval:** A node should be able to retrieve posts from its friends and friends-of-friends (up to a specified degree).
5.  **Gossip Protocol:** Implement a simple gossip protocol for post propagation. When a node creates a post, it should send it to all its friends. When a node receives a post, it should:
    *   Store the post in its cache (if space is available).
    *   Forward the post to its friends (except the sender, to avoid loops), only if the post is within the allowed degree.

**Constraints and Requirements:**

*   **Scalability:** The network should be able to handle a large number of nodes and posts.
*   **Limited Cache:** Each node has a limited cache size for storing posts. Implement a Least Recently Used (LRU) cache eviction policy.
*   **Degree-Limited Propagation:** Posts should only be propagated up to a specified degree of separation from the original author. This prevents the network from being flooded with posts. Degree 1 represents direct friends, Degree 2 represents friends-of-friends, etc.
*   **Eventual Consistency:** The network does *not* need to be perfectly consistent. It is acceptable for posts to take some time to propagate through the network, and for some nodes to not receive all posts.
*   **No Central Server:** The solution must be fully decentralized, with no central server or authority.
*   **Node IDs:** Node IDs are `u64` integers.
*   **Post IDs:** Post IDs are `u64` integers. Post IDs are globally unique (you don't need to enforce this, but your code should assume it).
*   **Post Content:** Post content is a `String`.
*   **Efficiency:** Aim for efficient algorithms and data structures to minimize latency and resource consumption. Consider the trade-offs between memory usage and processing time. The efficiency of your `post_retrieval` is especially important.
*   **Thread Safety:** The social network might have to deal with multiple threads accessing the data structures. Make sure to handle the race condition in a multi-threading environment properly.

**Function Signatures (Example):**

You are free to design your own data structures and function signatures, but here are some suggestions to get you started:

```rust
struct Node {
    id: u64,
    friends: Vec<u64>,
    post_cache: // Your LRU cache implementation,
    degree: u32 // max degree of posts to keep in cache
}

impl Node {
    fn new(id: u64, degree: u32) -> Self { /* ... */ }
    fn add_friend(&mut self, friend_id: u64) { /* ... */ }
    fn create_post(&self, post_id: u64, content: String) -> Post { /* ... */ }
    fn receive_post(&mut self, post: Post, sender_id: u64, current_degree: u32) { /* ... */ }
    fn get_posts(&self) -> Vec<Post> { /* ... */ }
}

struct Post {
    id: u64,
    author_id: u64,
    content: String,
    timestamp: u64, // e.g., UNIX timestamp
}

struct SocialNetwork {
    nodes: HashMap<u64, Node>, // id -> Node
    max_cache_size_per_node: usize,
}

impl SocialNetwork {
    fn new(max_cache_size_per_node: usize) -> Self { /* ... */ }
    fn create_node(&mut self, node_id: u64, degree: u32) { /* ... */ }
    fn connect_nodes(&mut self, node1_id: u64, node2_id: u64) { /* ... */ }
    fn post(&mut self, author_id: u64, post_id: u64, content: String) { /* ... */ }
    fn get_posts_for_node(&self, node_id: u64) -> Vec<Post> { /* ... */ }
}
```

**Note:** You don't need to implement a full P2P network simulation. You can assume a simplified environment where nodes can directly communicate with each other through function calls. The focus is on the core logic of post propagation, caching, and retrieval.
