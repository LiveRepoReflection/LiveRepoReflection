Okay, here's a challenging problem designed to test a range of skills, including graph algorithms, optimization, and handling potentially large datasets.

## Question: Distributed Transaction Validation Network

### Question Description

You are tasked with validating distributed transactions across a network of nodes. Each node holds a subset of the overall data and participates in transactions that may involve data held by other nodes. The goal is to determine, for a given transaction, whether it is *globally consistent* across the entire network, given limited communication capabilities and the potential for node failures.

The network consists of `N` nodes, numbered from `0` to `N-1`.  The network's topology is described by a list of bidirectional connections `connections`, where each connection is a tuple `(u, v)` indicating that node `u` is directly connected to node `v`.

Each node has the capability to:

1.  **Propose a transaction:** A transaction is represented as a list of data modifications. Each modification is a tuple `(node_id, key, old_value, new_value)`, where `node_id` is the ID of the node holding the data, `key` is the data key being modified, `old_value` is the value of the key before the transaction, and `new_value` is the intended value after the transaction.

2.  **Verify local consistency:** A node can verify whether the changes proposed for its own data (i.e., changes where `node_id` matches the node's ID) are consistent with its current data state.

3.  **Communicate with neighbors:** A node can send a limited amount of data to its directly connected neighbors.

4.  **Fail/Recover:** Nodes can fail (stop responding) and recover (start responding again) at any point. Your solution must be resilient to node failures.

Your task is to implement a function `is_transaction_consistent(network_size, connections, transaction_proposals, failed_nodes)` that takes the following inputs:

*   `network_size`: An integer representing the number of nodes in the network.
*   `connections`: A list of tuples representing the bidirectional connections between nodes. Each tuple is of the form `(u, v)` where `u` and `v` are node IDs.
*   `transaction_proposals`: A dictionary where keys are node IDs and values are lists of data modifications (`(node_id, key, old_value, new_value)` tuples) proposed by that node. Each node proposes only one transaction at a time.
*   `failed_nodes`: A set of node IDs that are currently considered failed (unresponsive).

The function should return `True` if the proposed transaction is globally consistent across the network, and `False` otherwise.

**Consistency Rules:**

1.  **Local Consistency:** Each node must be able to locally verify that the proposed changes to its data are valid (i.e., the `old_value` in each modification matches the current value of the data at that node). Failed nodes are considered to have inconsistent local data.
2.  **Global Agreement:** All non-failed nodes must agree on the outcome of the transaction. Due to the distributed nature, nodes can only directly communicate with their neighbors. You must devise a strategy for nodes to reach a consensus, even with node failures.
3.  **Transaction Atomicity:** A transaction is considered valid if and only if all proposed changes can be successfully applied without violating any data constraints.

**Constraints:**

*   **Network Size (N):** 1 <= N <= 1000
*   **Number of Connections:** 0 <= Number of Connections <= N\*(N-1)/2
*   **Transaction Size:** 0 <= Number of modifications per transaction <= 100
*   **Communication Limitations:**  Nodes can only communicate directly with their immediate neighbors.  Minimize the amount of data exchanged between nodes to avoid network congestion.
*   **Node Failures:** The set of `failed_nodes` can change between transaction validation requests. Your solution must be resilient to node failures and recoveries.
*   **Data State:** You are not provided with the initial data state of each node. You can only infer the data state based on the `old_value` and `new_value` in the `transaction_proposals` and previous outcomes.
*   **Time Complexity:** Your solution should aim for the best possible time complexity, considering the constraints. Inefficient algorithms may time out during evaluation.

**Example:**

Let's say you have 3 nodes (0, 1, 2) connected as follows: `connections = [(0, 1), (1, 2)]`.
Node 0 proposes: `[(0, "x", 5, 10)]` (change key "x" from 5 to 10)
Node 1 proposes: `[(1, "y", 20, 25)]` (change key "y" from 20 to 25)
Node 2 proposes: `[(2, "z", 100, 105)]` (change key "z" from 100 to 105)
`failed_nodes = set()`

If the transaction is globally consistent, the function should return `True`. If, for example, node 1's current value for "y" is not 20, or if the communication protocol fails to reach a consensus, the function should return `False`.

**Scoring:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The solution must correctly determine the global consistency of transactions under various network topologies, transaction proposals, and failure scenarios.
*   **Efficiency:** The solution should minimize the amount of communication between nodes and optimize the time complexity of the algorithm.
*   **Robustness:** The solution should be robust to node failures and recoveries.
*   **Scalability:** The solution should scale well to larger networks.

This problem requires you to think about distributed systems, consensus algorithms (even if a simplified version), and how to handle failures in a distributed environment. Good luck!
