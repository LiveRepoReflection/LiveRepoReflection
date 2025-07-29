## Problem: Decentralized Identity Graph Synchronization

**Description:**

Imagine a globally distributed, decentralized identity system. This system consists of numerous independent "Identity Providers" (IdPs). Each IdP maintains a directed graph representing relationships between users within its domain.  These graphs are inherently local; however, users across different IdPs can establish relationships with each other, creating a global, interconnected identity graph.

Each IdP exposes an API to query the relationships originating from its users.  Specifically, given a user ID within that IdP's domain, the API returns a list of user IDs (potentially from *any* IdP) that the given user "follows" or is directly connected to.  This API is rate-limited and has a cost associated with each call, representing computational resources and network bandwidth.

Your task is to design an algorithm that, given a starting user ID (within a known IdP), efficiently discovers all users within a *specified "k-hop" radius* of that starting user in the global identity graph.  "k-hop" means traversing at most *k* edges (relationships).

**Constraints & Requirements:**

1.  **Decentralization:** You cannot assume access to a central database or any global view of the graph. You *must* interact with the IdPs' APIs to discover relationships.

2.  **API Access:** You are given a function `get_follows(idp_name, user_id)`, which simulates an IdP's API.  It takes the IdP's name (string) and a user ID (string) as input and returns a list of user IDs (strings) that the given user follows. Each user ID is formatted as "user@idp", e.g., "alice@idp1".  The function call has a cost of 1 unit.  The cost should be minimized.

3.  **IdP Discovery:** You are *not* given a list of all IdPs.  You must discover them dynamically as you traverse the graph.

4.  **Optimality:** Your solution must minimize the number of calls to `get_follows(idp_name, user_id)`. Redundant calls are heavily penalized. Consider that the global identity graph may be very large, so efficiency is crucial. Avoid exploring the same users multiple times.

5.  **Scalability:** Your algorithm should be able to handle a large number of users and IdPs.  Avoid storing the entire graph in memory if possible.

6.  **Rate Limiting Simulation:** Assume the `get_follows` API also simulates rate limits. When `get_follows` is called too frequently, it can raise `RateLimitExceeded` exception, so you need to handle this exception and retry the failed API call.

7.  **Edge Cases:** Handle cases where a user follows themselves, circular dependencies exist, and the graph is sparsely connected.

8.  **Cost Function:** The primary metric is the number of calls to `get_follows()`. Your goal is to find *all* reachable users within *k* hops while making the *fewest* possible API calls.

**Input:**

*   `start_user`: A string representing the starting user ID in the format "user@idp".
*   `k`: An integer representing the maximum number of hops to traverse.

**Output:**

*   A set of strings representing all user IDs (in "user@idp" format) reachable from `start_user` within `k` hops (inclusive). The `start_user` should be included in the output.

**Example:**

If `start_user` is "alice@idp1" and `k` is 2, your algorithm should return all users reachable from "alice@idp1" within 2 hops.

**This problem requires a combination of graph traversal, API interaction, cost optimization, and careful handling of constraints and edge cases. Good luck!**
