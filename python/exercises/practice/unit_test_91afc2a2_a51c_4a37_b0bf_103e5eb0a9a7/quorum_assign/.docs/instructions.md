## Question: Optimizing the Distributed Transaction Log

### Question Description

You are designing a highly available and scalable distributed database system. A critical component is the distributed transaction log, which ensures data consistency across multiple nodes. Each transaction generates a log entry that must be durably stored on a quorum of nodes before the transaction can be considered committed.

The system consists of `N` nodes, numbered from `0` to `N-1`. Each log entry has a unique ID (an integer). For each transaction, the system selects a *write quorum* of `K` distinct nodes (where `1 <= K <= N`). A log entry must be written to all nodes in its write quorum before the transaction can be considered committed.

The system uses a centralized coordinator node to manage the write quorums. The coordinator maintains a list of available nodes and dynamically assigns write quorums to each transaction. The coordinator must balance the load across the nodes while minimizing the potential for conflicts.

**Challenge:**

Implement a function `assign_quorums(N, K, transactions)` that efficiently assigns write quorums to a sequence of transactions, given the number of nodes `N`, the quorum size `K`, and a list of `transactions` (each transaction is represented simply by a unique integer ID).

The function should return a list of tuples, where each tuple represents the assigned write quorum for a transaction. Each tuple should contain the transaction ID and a set (or list) of `K` distinct node IDs (integers from `0` to `N-1`).

**Requirements and Constraints:**

1.  **Load Balancing:** The assignments should aim to distribute the write load as evenly as possible across all `N` nodes.  Minimize the maximum number of transactions assigned to any single node.
2.  **Conflict Minimization:** While perfect conflict avoidance is impossible, try to avoid assigning the same node to the write quorums of transactions that are likely to be executed concurrently.  Assume the transactions in the input list `transactions` are ordered by their arrival time, and transactions close to each other in the list are more likely to be executed concurrently.
3.  **Distinct Nodes:** Each write quorum must consist of `K` *distinct* nodes.
4.  **Valid Node IDs:** Node IDs must be integers in the range `[0, N-1]`.
5.  **Efficiency:** The solution should be efficient enough to handle a large number of nodes and transactions. Aim for a time complexity significantly better than O(transactions * N^K) (i.e., avoid brute force enumeration of all possible quorums).
6.  **Deterministic Behavior:** For a given input (`N`, `K`, `transactions`), the function should always return the same output. This is crucial for testing and debugging.
7.  **Fault Tolerance Consideration**: Try to avoid having always the same K nodes being selected for a quorum to increase fault tolerance.

**Input:**

*   `N` (int): The number of nodes in the system. `1 <= N <= 1000`
*   `K` (int): The quorum size. `1 <= K <= N`
*   `transactions` (list of int): A list of transaction IDs. The length of the list can be up to `10000`.

**Output:**

*   `list of tuples`: A list of tuples, where each tuple is in the format `(transaction_id, quorum)`, where `quorum` is a list of node IDs (integers).

**Example:**

```python
N = 5
K = 3
transactions = [101, 102, 103, 104, 105]

result = assign_quorums(N, K, transactions)

# Possible output (order of nodes in the quorum may vary):
# [(101, [0, 1, 2]), (102, [1, 2, 3]), (103, [2, 3, 4]), (104, [3, 4, 0]), (105, [4, 0, 1])]
```
