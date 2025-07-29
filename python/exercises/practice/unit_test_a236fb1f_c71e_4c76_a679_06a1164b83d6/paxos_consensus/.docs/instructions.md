## Problem Title: Distributed Consensus via Paxos Simulation

### Problem Description:

You are tasked with simulating a simplified version of the Paxos distributed consensus algorithm. You will model a cluster of nodes attempting to agree on a single value (e.g., a transaction to commit, a configuration update).

The cluster consists of `N` nodes, where `N` is an odd number (to ensure a majority). Each node can act as a Proposer, Acceptor, and Learner.

**Simplified Paxos Roles:**

*   **Proposer:** Proposes a value with a unique proposal number (integer).
*   **Acceptor:** Responds to proposers. Keeps track of the highest proposal number it has seen and the value accepted for that proposal number (if any).
*   **Learner:** Obtains the agreed-upon value after consensus is reached.

**Simplified Paxos Protocol:**

1.  **Prepare Phase:**
    *   A Proposer chooses a proposal number `n` (which must be higher than any number it has used before) and sends a "Prepare" request to all Acceptors.
2.  **Promise Phase:**
    *   An Acceptor, upon receiving a "Prepare" request with proposal number `n`:
        *   If `n` is higher than any proposal number the Acceptor has seen so far, it promises to ignore any future "Prepare" requests with a lower number. The acceptor also sends back to the proposer the highest proposal number it has accepted so far (if any) and the corresponding accepted value.
        *   If `n` is not higher than any proposal number the Acceptor has seen so far, it ignores the request.
3.  **Accept Phase:**
    *   If a Proposer receives promises from a majority of Acceptors:
        *   If any Acceptor has accepted a value, the Proposer proposes the value associated with the highest proposal number reported by the Acceptors.
        *   Otherwise, the Proposer proposes its original value.
        *   The Proposer sends an "Accept" request with the chosen proposal number and value to all Acceptors.
4.  **Accepted Phase:**
    *   An Acceptor, upon receiving an "Accept" request with proposal number `n`:
        *   If `n` is the highest proposal number the Acceptor has seen so far, it accepts the value and stores the proposal number and value. The Acceptor sends back an "Accepted" message to all Learners (in this simplified version, we can assume it sends the message back to the Proposer as well).
        *   Otherwise, it ignores the request.
5.  **Learning:**
    *   A value is considered "learned" when a majority of Acceptors have accepted it. In this simplified model, assume the Proposer that initiated the accepted phase also acts as a Learner and determines when consensus is reached.

**Your Task:**

Implement a simulation of the simplified Paxos algorithm. Your code should:

1.  Take as input:
    *   `N`: The number of nodes in the cluster (an odd integer >= 3).
    *   `proposals`: A list of tuples, where each tuple represents a proposal attempt by a Proposer: `(proposer_id, proposed_value)`. The `proposer_id` is an integer between `0` and `N-1` and `proposed_value` can be any comparable value (e.g., integers, strings).
2.  Simulate the Paxos protocol. Each proposer generates unique increasing proposal numbers.
3.  Determine if a consensus is reached.
4.  Return:
    *   The agreed-upon value if consensus is reached.
    *   `None` if consensus is not reached after processing all proposals.

**Constraints and Considerations:**

*   **Node Failures:** Nodes can fail. Model node failures as a percentage chance of a node failing to respond to a "Prepare" or "Accept" request.  The failure rate should be a parameter to your simulation (e.g., `failure_rate = 0.1` means a 10% chance of a node failing to respond). A node remains failed for the entire simulation.
*   **Message Loss:** Messages between nodes can be lost. Model message loss as a percentage chance of a message being lost in transit. The message loss rate is also a parameter to the simulation.
*   **Proposal Numbers:** Proposers must generate unique, monotonically increasing proposal numbers.  You can assume a proposer keeps track of its highest proposal number seen so far.
*   **Majority:** Consensus requires a strict majority (more than 50%) of the Acceptors.
*   **Efficiency:** While this is a simulation, aim for reasonable efficiency in your code. Avoid unnecessary computations or data structures.
*   **Determinism (Important):**  Because of the random factors introduced by node failures and message loss, getting consistent results across multiple runs is difficult.  To make the problem more deterministic, you **must** use a fixed seed for your random number generator (e.g., `random.seed(42)`). This allows us to test your algorithm with predictable outcomes given the same input parameters.

**Example:**

```python
N = 3
proposals = [(0, 10), (1, 20), (0, 30)] # (proposer_id, proposed_value)

agreed_value = paxos_simulation(N, proposals, failure_rate=0.1, message_loss_rate=0.05)

# Possible outcome: agreed_value = 10 (if proposer 0 succeeds with its first proposal)
# or agreed_value = 20 or agreed_value = 30 or agreed_value = None (if no consensus is reached)
```

**Hints:**

*   Start by implementing the core Paxos logic without node failures or message loss.
*   Gradually add the failure and message loss simulations.
*   Use appropriate data structures to represent the state of each node (e.g., dictionaries to store accepted values, highest proposal numbers seen).
*   Consider using logging or debugging statements to trace the execution of your simulation.

This problem requires a good understanding of the Paxos algorithm and careful consideration of edge cases and potential failure scenarios. Good luck!
