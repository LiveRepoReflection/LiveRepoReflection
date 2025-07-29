## Problem Title: Decentralized Load Balancer Simulation

### Question Description:

You are tasked with simulating a decentralized load balancer for a distributed service. The service consists of `N` identical servers, each capable of handling a certain number of requests per second. Incoming requests arrive at a central dispatcher, which needs to distribute them among the available servers.  However, the dispatcher is not a single, centralized entity. Instead, it is a collection of `M` independent dispatch nodes, each with a partial view of the server state.

Each dispatch node maintains a local, potentially outdated, view of the current load (number of requests being processed) on each server.  When a dispatch node receives a batch of requests, it must decide how to distribute them to the servers, aiming to minimize the overall latency and prevent any server from being overloaded. Since the information is not consistent across all dispatch nodes, conflicting decisions may occur, resulting in suboptimal load distribution.

**Specifics:**

1.  **Servers:** There are `N` servers, indexed from 0 to `N-1`. Each server `i` has a maximum capacity `C[i]` (requests per second).
2.  **Dispatch Nodes:** There are `M` dispatch nodes, indexed from 0 to `M-1`.
3.  **Request Batches:** Requests arrive in batches. Each batch is routed to a single, randomly selected dispatch node.
4.  **Dispatch Node State:** Each dispatch node `j` maintains a local view `L[j][i]` representing its estimate of the current load on server `i`. `L[j][i]` is initialized to 0 for all `i` and `j`.
5.  **Request Distribution:** When a dispatch node `j` receives a batch of `R` requests, it must decide how many requests `D[j][i]` to send to each server `i`. The distribution must satisfy the following constraints:
    *   `sum(D[j][i] for i in range(N)) = R`  (All requests in the batch must be distributed.)
    *   `0 <= D[j][i] <= C[i] - L[j][i]` (No server can be overloaded, according to the dispatch node's local view.)
    *   `D[j][i]` must be an integer.
6.  **State Update:** After a dispatch node `j` distributes a batch of requests, it updates its local view: `L[j][i] = L[j][i] + D[j][i]` for all `i`.
7. **Load Propagation**: After each batch distribution, simulate a gossip protocol. Each Dispatch Node randomly selects `K` other dispatch nodes (with replacement) and averages its load state with each selected node, i.e. if node `a` selects node `b`, then for all servers `i`, `L[a][i] = (L[a][i] + L[b][i]) / 2` and `L[b][i] = (L[b][i] + L[a][i]) / 2`.

**Goal:**

Write a function `simulate_load_balancing(N, M, C, request_batches, K)` that simulates this decentralized load balancing system. The function should return the *maximum* load observed on any server at any point during the simulation.

**Input:**

*   `N`: (int) The number of servers.
*   `M`: (int) The number of dispatch nodes.
*   `C`: (list of int) A list of length `N` representing the capacity of each server.
*   `request_batches`: (list of int) A list where each element represents the size of a request batch.
*   `K`: (int) The number of other dispatch nodes each node averages its load state with during the gossip protocol.

**Output:**

*   (int) The maximum load observed on any server across all simulation steps. The load on a server is the sum of requests currently being processed by it.

**Constraints:**

*   `1 <= N <= 100`
*   `1 <= M <= 100`
*   `1 <= C[i] <= 1000` for all `i`
*   `1 <= len(request_batches) <= 1000`
*   `1 <= request_batches[i] <= 1000` for all `i`
*   `0 <= K <= M - 1`
*   Your solution must be efficient enough to handle the maximum input sizes. Inefficient algorithms may time out.
*   The request distribution strategy within each dispatch node should strive to balance the load effectively to minimize the maximum server load and prevent overloads.

**Example:**

```python
N = 3
M = 2
C = [100, 120, 150]
request_batches = [50, 80, 60, 40, 70]
K = 1

max_load = simulate_load_balancing(N, M, C, request_batches, K)
print(max_load) # Output: An integer representing the maximum server load during the simulation.
```

**Judging Criteria:**

Your solution will be judged on correctness, efficiency, and code clarity.  Emphasis will be placed on handling the constraints effectively and minimizing the maximum server load. Solutions that lead to frequent server overloads (even if temporary) will be penalized.

**Hint:**

Consider strategies for request distribution within each dispatch node.  A simple round-robin approach might not be optimal. Think about how to balance the load based on the dispatch node's local view of server capacity and current load. Remember that the gossip protocol is designed to eventually synchronize the dispatch node states, which should help load balancing over time.

Good luck!
