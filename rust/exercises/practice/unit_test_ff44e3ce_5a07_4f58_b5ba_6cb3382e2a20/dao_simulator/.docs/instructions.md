## Problem: Decentralized Autonomous Organization (DAO) Simulation

**Problem Description:**

You are tasked with building a simplified simulation of a Decentralized Autonomous Organization (DAO) operating on a blockchain. The DAO manages a treasury of ERC-20 tokens and allows members to submit and vote on proposals to spend these tokens.

**Core Functionality:**

1.  **Member Management:** The DAO has a dynamic set of members, each identified by a unique address (represented as a `String`). Members have voting rights.

2.  **Proposal Submission:** Members can submit proposals to spend tokens from the treasury. A proposal includes:
    *   A unique ID (represented as a `u64`).
    *   The proposer's address.
    *   The recipient address for the tokens.
    *   The amount of tokens to be transferred.
    *   A description of the proposal (represented as a `String`).

3.  **Voting:** Members can vote "yes" or "no" on active proposals. Each member can only vote once per proposal.

4.  **Quorum:** A proposal passes only if it meets a minimum quorum, defined as a percentage of the total number of members that must vote.

5.  **Threshold:** A proposal passes if at least a threshold of the votes cast are "yes" votes.

6.  **Execution:** If a proposal passes, the specified amount of tokens is transferred from the DAO's treasury to the recipient address.

7.  **Transaction Simulation:** Implement a simplified transaction simulation. Assume that all transactions within the DAO simulation are atomic and consistent. When a proposal passes, the token transfer happens instantly.

**Data Structures:**

You will need to design suitable data structures to represent:

*   Members
*   Proposals (including their status, votes, etc.)
*   The DAO's treasury balance
*   The blockchain state (e.g., block number, transaction history - simplified as proposal history)

**Constraints and Requirements:**

*   **Gas Efficiency:** In a real blockchain environment, gas costs (computation costs) are a major concern. While you're not directly dealing with gas, strive for efficient data structures and algorithms to minimize computational overhead. Consider the time complexity of your operations.
*   **Concurrency:** Assume that multiple members can submit proposals and vote concurrently. Ensure your implementation is thread-safe.
*   **Immutability:** While this is a simulation, try to emulate some aspects of blockchain immutability. For example, once a vote is cast, it cannot be changed.
*   **Edge Cases:** Handle edge cases gracefully. For example:
    *   Submitting a proposal with an invalid recipient address.
    *   Voting on a non-existent proposal.
    *   Voting multiple times on the same proposal.
    *   Attempting to execute a proposal with insufficient treasury balance.
    *   Handling integer overflows when calculating vote counts or treasury balances.
*   **Scalability:** Consider how your solution would scale as the number of members and proposals increases. Think about the data structures you choose and how they impact performance.
*   **Security:** Prevent malicious actors from manipulating the voting process (e.g., double voting, voting with non-existent accounts).

**Specific Instructions:**

Implement the following functions within your DAO simulation:

*   `add_member(address: String)`: Adds a new member to the DAO.
*   `submit_proposal(proposer: String, recipient: String, amount: u64, description: String)`: Submits a new proposal.  Returns the proposal ID.
*   `vote(proposal_id: u64, voter: String, vote: bool)`: Allows a member to vote on a proposal (true for "yes", false for "no").
*   `execute_proposal(proposal_id: u64)`: Executes a proposal if it has passed and is executable (enough funds in treasury).
*   `get_treasury_balance()`: Returns the current balance of the DAO treasury.
*   `get_proposal_status(proposal_id: u64)`: Returns the status of a proposal (e.g., "Pending", "Passed", "Failed", "Executed").

**Bonus Challenges:**

*   Implement a reputation system where members gain or lose reputation based on the success or failure of proposals they submit.  Reputation can influence voting power.
*   Add support for delegated voting, allowing members to delegate their voting power to another member.
*   Implement a time-locking mechanism where proposals can only be executed after a certain time period has elapsed.

This problem is designed to be challenging and open-ended, allowing you to explore different design choices and optimization techniques. The focus is on creating a robust, efficient, and secure simulation of a DAO. Good luck!
