Okay, here's a challenging and sophisticated Python coding problem designed for a high level of difficulty:

**Problem Title: Decentralized Transaction Validator Network**

**Problem Description:**

You are tasked with designing and implementing a simplified, yet robust, decentralized transaction validation network. This network simulates a blockchain-like system where transactions are proposed, validated by multiple nodes, and then committed to a distributed ledger.

The network consists of `N` validator nodes. Each node has a unique ID (an integer from 0 to N-1), a computational power score and maintains a partial view of the overall network state.

Transactions are represented as strings. A valid transaction transforms the global state (initially an empty string) in a deterministic way. The transformation is simulated by SHA-256 hashing. Appending the transaction string to the current global state, and computing the SHA-256 hash of the result, yields the new global state.

The network operates in discrete rounds. Each round consists of the following steps:

1.  **Transaction Proposal:** One node, chosen randomly, proposes a new transaction to the network.
2.  **Validation:** Each node independently validates the proposed transaction.
    *   A transaction is considered valid by a node if applying it to the node's current view of the global state results in a valid state transition (as described above). Critically, each node might have a different view of the global state due to network latency and asynchronicity.
    *   Furthermore, each node has a probability of making an incorrect validation decision. The probability of incorrect validation is inversely proportional to its computational power.
3.  **Consensus:** Nodes broadcast their validation decision (valid or invalid) to the network.
4.  **Commitment:** Based on the received validation decisions, each node independently determines whether to commit the transaction to its local ledger.
    *   A node commits the transaction if a weighted majority of the validators consider the transaction valid. The weight of each validator is its computational power.
    *   If a transaction is committed, the node updates its local view of the global state by applying the transaction.

Your goal is to implement the core logic of this network.

**Specific Requirements:**

1.  **Node Class:** Implement a `Node` class with the following methods:
    *   `__init__(self, node_id, computational_power, network_size)`: Initializes the node with its ID, computational power, the total number of nodes in the network.
    *   `propose_transaction(self, transaction_content)`: Proposes a new transaction given the content to the network. Only the elected node can propose the transaction.
    *   `validate_transaction(self, transaction_content, current_global_state)`: Validates a proposed transaction against the node's current view of the global state and returns `True` if valid, `False` otherwise. The node has a chance to make mistake based on the computational power.
    *   `commit_transaction(self, transaction_content, validation_results)`: Determines whether to commit the transaction based on the validation results from other nodes and the weighted majority rule. Updates the node's local view of the global state if the transaction is committed.
    *   `get_global_state(self)`: Returns the node's current view of the global state.

2.  **Simulation Function:** Implement a function `simulate_network(nodes, transactions)` that simulates the network for a given list of transactions. The function should take a list of `Node` objects and a list of transaction content strings as input. The function should return the final global state for each node in the network.

**Constraints and Edge Cases:**

*   **Asynchronous Network:** Nodes do not have a consistent view of the network state.
*   **Weighted Majority:** The commitment decision must be based on the computational power of the validators.
*   **Byzantine Fault Tolerance (Simplified):** Nodes can make incorrect validation decisions. The network should still be reasonably resilient to these faulty nodes.
*   **Deterministic Hashing:** Use SHA-256 hashing for state transitions. Use a standard Python library for SHA-256.
*   **Computational Power and Validation Accuracy:** Higher computational power should translate to a lower probability of incorrect validation. The exact relationship is up to you, but it should be reasonable.
*   **Randomness:** The transaction proposer should be chosen randomly in each round. Use a proper random number generator.
*   **Scalability:** Consider how your design would scale to a larger number of nodes.
*   **Network Latency (Implicit):** Assume that validation results are not instantly available to all nodes.  Each node makes its commit decision based on the validation results it has *received* by the end of the round. Nodes might not receive all validation results due to latency.
*   **No Central Authority:** There is no central coordinator or trusted third party.  Each node operates independently.

**Optimization Requirements:**

*   **Algorithmic Efficiency:** The validation and commitment logic should be efficient, especially for a large number of nodes.
*   **Memory Usage:** The solution should be memory-efficient, as the global state could potentially grow large over time.

**Real-World Relevance:**

This problem simulates the core challenges of building a decentralized, fault-tolerant system.  It touches upon consensus algorithms, distributed ledgers, and Byzantine fault tolerance – all critical concepts in blockchain technology.

**Difficulty Justification:**

This problem is challenging because it requires a deep understanding of distributed systems concepts, careful consideration of edge cases, and efficient implementation of complex logic. The need to handle asynchronous states, weighted majority consensus, and potential node failures makes this a genuinely hard problem. The scalability requirement also forces the candidate to think about efficient data structures and algorithms.
