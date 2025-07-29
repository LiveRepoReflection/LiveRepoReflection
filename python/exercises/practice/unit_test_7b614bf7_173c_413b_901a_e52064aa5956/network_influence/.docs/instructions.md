## Problem: Decentralized Social Network Analytics

**Question Description:**

You are tasked with developing a system to analyze a decentralized social network. This network is structured as a peer-to-peer (P2P) graph, where each user (node) maintains connections (edges) to a subset of other users. Due to the decentralized nature, there's no central server holding the complete graph. Each user only knows their direct connections.

Your system needs to efficiently calculate the "influence score" of a given user within this network. The influence score is defined as the weighted sum of the reachability of that user to all other users, considering the path lengths.

**Specifically:**

1.  **Network Representation:** Assume you have access to a function `get_connections(user_id)` that returns a list of `user_id`s representing the direct connections of a given user. This function simulates querying a specific user's node in the P2P network. The network is undirected (if A is connected to B, B is connected to A).

2.  **Reachability:** The reachability of user A to user B is calculated as `1 / (path_length + 1)`. If there's no path between A and B, the reachability is 0.  The `path_length` is the minimum number of hops between A and B.

3.  **Influence Score:** The influence score of user A is the sum of reachabilities from user A to all other users in the network.

4.  **Global Network Size:** You are given an estimate `N` of the total number of users in the network (1 <= N <= 10000). This is an estimate, not a guarantee of the exact number of users. User IDs are integers, and while you can assume user IDs will generally be in the range `[0, 2*N]`, you must handle cases where users outside of this range exist within the network.

5.  **Optimization Requirement:**  Due to the decentralized nature and the potentially large network size, fetching all connections at once is infeasible. You need to minimize the number of calls to the `get_connections(user_id)` function.  Solutions that aggressively call this function for every possible user will likely time out.

6.  **Edge Cases:**
    *   Disconnected components: The network may not be fully connected.
    *   "Ghost" users: User IDs might exist that are not actually connected to any other users.  Calling `get_connections()` on them should return an empty list.
    *   Cycles: The graph can contain cycles.
    *   Duplicate connections: The `get_connections()` function may return duplicate user IDs (your solution must handle this).
    *   Self-loops: The `get_connections()` function may return the user's own ID.

7.  **Efficiency:** Your solution should be efficient in terms of both time and the number of calls to `get_connections(user_id)`.  The judge will run your code against a variety of test cases with different network topologies and user counts. Test cases are designed to differentiate correct but inefficient solutions from truly optimized ones. Solutions exceeding a reasonable time limit or making excessive calls to `get_connections()` will fail.

**Your Task:**

Write a function `calculate_influence_score(user_id, N, get_connections)` that takes a `user_id` (the user for whom to calculate the influence score), an estimate `N` of the network size, and the `get_connections` function as input.  The function should return the calculated influence score for the given user.

**Constraints:**

*   Time limit: A reasonable time limit will be enforced during judging.
*   Call limit:  A limit will be placed on the maximum number of calls to the `get_connections` function.
*   1 <= N <= 10000
*   User IDs are integers.

**Example:**

```python
def get_connections_example(user_id):
  # A simple example network for demonstration purposes
  if user_id == 1:
    return [2, 3]
  elif user_id == 2:
    return [1, 4]
  elif user_id == 3:
    return [1]
  elif user_id == 4:
    return [2]
  else:
    return []

N = 4  # Estimated network size
user_id = 1
influence_score = calculate_influence_score(user_id, N, get_connections_example)
print(f"Influence score of user {user_id}: {influence_score}")
```

This problem emphasizes graph traversal, optimization strategies, and handling real-world constraints of a decentralized system. A naive solution using BFS or DFS without considering the call limit to `get_connections` will likely fail.  Efficient solutions might involve techniques like iterative deepening, intelligent connection sampling, or approximation algorithms. Good luck!
