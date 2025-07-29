Okay, here's a challenging Python coding problem designed to test advanced knowledge and optimization skills.

### Project Name

`OptimalNetworkClustering`

### Question Description

You are tasked with designing an efficient algorithm for clustering nodes in a dynamic network. The network represents a social network where nodes are users and edges represent relationships between users. The network evolves over time, with users joining, leaving, and relationships changing.

Specifically, you are given a stream of events representing changes to the network. Each event is one of the following types:

*   `"add_user", user_id`: Adds a new user with the given `user_id` to the network. User IDs are unique positive integers.
*   `"remove_user", user_id`: Removes the user with the given `user_id` from the network. If the user does not exist, the event is ignored. Removing a user also removes all their relationships.
*   `"add_relationship", user_id1, user_id2`: Adds a relationship between `user_id1` and `user_id2`. Relationships are undirected and reciprocal. If either user does not exist, the event is ignored. If the relationship already exists, the event is ignored.
*   `"remove_relationship", user_id1, user_id2`: Removes the relationship between `user_id1` and `user_id2`. If either user or the relationship does not exist, the event is ignored.

Your algorithm must maintain a clustering of the network such that users in the same cluster are highly interconnected. To quantify the quality of the clustering, we define a metric called "Cluster Density."

**Cluster Density:** For a cluster C, the cluster density is defined as:

`density(C) = (2 * number_of_edges_within_C) / (number_of_nodes_in_C * (number_of_nodes_in_C - 1))`

If `number_of_nodes_in_C` is less than 2, the density is 0.

Your goal is to maintain clusters such that each cluster has a density of at least `min_density`.

**Constraints and Requirements:**

*   **Efficiency:** The algorithm must be efficient in handling a large number of events (up to 10^6 events) and a large number of users (up to 10^5 users).  The target complexity is *O(log n)* per event, where *n* is the number of users.
*   **Minimum Density:** You must ensure that all clusters maintained by your algorithm have a density of at least `min_density` (a float between 0 and 1, inclusive). If, after an event, a cluster's density falls below `min_density`, you must split the cluster or merge it with other clusters to maintain this constraint. It is always possible to form clusters that satisfy this constraint.
*   **Clustering Strategy:** You are free to choose the clustering strategy. A good strategy should aim to minimize the number of clusters while maintaining the density constraint. Common strategies include:
    *   Merging clusters that, when combined, still meet the density requirement.
    *   Splitting a cluster into smaller, denser clusters if its density falls below the threshold.
*   **Initial State:** Initially, the network is empty (no users or relationships).
*   **Output:** After processing each event, your algorithm must return a list of sets, where each set represents a cluster and contains the `user_id`s of the users in that cluster. The order of the clusters in the list is not important, and the order of `user_id`s within a cluster is also not important.
*   **Implementation Details:**
    *   Assume that all `user_id`s are valid positive integers.
    *   You can use any standard Python libraries.
    *   Your code will be tested against a variety of event sequences, including edge cases and large datasets.
*   **min_density:** This value will be provided to your class during initialization.

**Input:**

A list of events, where each event is a tuple: `(event_type, *args)`.

**Example:**

```python
events = [
    ("add_user", 1),
    ("add_user", 2),
    ("add_relationship", 1, 2),
    ("get_clusters",),
    ("add_user", 3),
    ("add_relationship", 1, 3),
    ("get_clusters",),
    ("remove_relationship", 1, 2),
    ("get_clusters",),
]
```

**Expected Output (with min_density = 0.5, for example):**

```
[
    [{1}, {2}], #After add_user 1 and 2
    [{1, 2}], #After add_relationship 1, 2
    [{1, 2}],
    [{3}, {1, 2}], #After add_user 3
    [{1, 2, 3}], #After add_relationship 1, 3
    [{1, 2, 3}],
    [{3}, {1}, {2}], #After remove_relationship 1, 2
    [{3}, {1}, {2}],
]
```

**Write a class `NetworkClustering` with the following methods:**

*   `__init__(self, min_density: float)`: Initializes the class with the given `min_density`.
*   `process_event(self, event: tuple) -> list[set[int]]`: Processes the given event and returns the current list of clusters.
*   `get_clusters(self) -> list[set[int]]`: Returns the current list of clusters.  This can be called directly or as part of processing an event.

This problem requires a combination of graph data structures, clustering algorithms, and careful optimization to meet the efficiency requirements. Good luck!
