## Question: Decentralized Autonomous Organization (DAO) Voting Simulation

**Description:**

You are tasked with building a simulation of a voting system for a Decentralized Autonomous Organization (DAO). The DAO manages a significant treasury and makes decisions through proposals voted on by its members. Your goal is to implement a robust and scalable voting system that accounts for various real-world complexities.

**System Requirements:**

1.  **Weighted Voting:** Each member has a voting weight based on the amount of governance tokens they hold. The weight is represented as a `uint64`.

2.  **Proposal Creation:** Members can submit proposals. Each proposal has a unique ID, a description, and a deadline (represented as a Unix timestamp in seconds).

3.  **Voting Process:**
    *   Members can cast their votes (For, Against, Abstain) on active proposals before the deadline.
    *   A member can only vote once per proposal.
    *   Votes should be recorded along with the voter's weight at the time of voting.

4.  **Tallying Votes:** After the deadline, the votes are tallied to determine the outcome of the proposal.

5.  **Quorum Requirement:** A proposal must reach a minimum quorum of total voting weight to be considered valid.  This quorum is a percentage (given as an integer between 0-100) of the total possible voting weight in the DAO.

6.  **Passing Threshold:** A proposal must receive a minimum percentage (given as an integer between 0-100) of 'For' votes out of the total 'For' and 'Against' votes to pass. Abstain votes are not included in the threshold calculation.

7.  **Dynamic Membership:** Members can join or leave the DAO at any time, and their voting weight can change as they acquire or sell governance tokens. The system must handle these changes efficiently.

8.  **Scalability:** The DAO has a large and growing membership. The system must be designed to handle a significant number of members, proposals, and votes.

9.  **Concurrency:** Multiple members may be voting or submitting proposals concurrently. Your solution needs to be thread-safe.

10. **Time-Based Voting Power:** A member's voting power is determined by the amount of tokens they hold *at the time of the vote*. If a member's token balance changes after they vote, it does NOT affect their recorded vote weight.

**Input:**

Your solution should accept a sequence of operations. These operations represent member actions, system events, and queries.

The operations include:

*   `"CREATE_PROPOSAL proposal_id deadline description"`: Creates a new proposal with the given ID, deadline, and description.
*   `"VOTE proposal_id member_id vote weight"`: A member casts their vote on a proposal (vote: "FOR", "AGAINST", or "ABSTAIN"). The weight is the member's voting weight at the time of voting.
*   `"GET_RESULT proposal_id"`: Returns the result of the proposal after the deadline has passed.
*   `"SET_QUORUM quorum_percentage"`: Sets the quorum percentage for the DAO.
*   `"SET_THRESHOLD threshold_percentage"`: Sets the passing threshold percentage for the DAO.

**Output:**

For each `"GET_RESULT proposal_id"` operation, your solution should output one of the following:

*   `"PASS"`: The proposal passed.
*   `"REJECT"`: The proposal was rejected.
*   `"QUORUM_NOT_MET"`: The proposal did not meet the quorum requirement.
*   `"PENDING"`: The proposal deadline has not passed yet.
*   `"INVALID_PROPOSAL"`: The proposal does not exist.

**Constraints:**

*   The number of members and proposals can be very large (up to 10^6).
*   The number of votes can be even larger (up to 10^7).
*   Proposal IDs are unique integers.
*   Member IDs are unique integers.
*   Voting weights are non-negative integers (uint64).
*   Deadlines are Unix timestamps in seconds.
*   Quorum and threshold percentages are integers between 0 and 100.
*   The current time can be simulated by incrementing a global clock. You need to ensure your solution respects the simulated time when determining if a proposal is past its deadline. You can assume a global function `getCurrentTime()` exists that returns the current simulated Unix timestamp.
*   The solution must be thread-safe.

**Example:**

```
// Input Operations
CREATE_PROPOSAL 1 1678886400 "Increase treasury spending"
VOTE 1 1 FOR 100
VOTE 1 2 AGAINST 50
GET_RESULT 1 // Assuming current time > 1678886400, and default quorum/threshold are met.

// Expected Output: PASS
```

**Evaluation Criteria:**

*   **Correctness:** The solution must accurately simulate the voting process and return the correct results.
*   **Efficiency:** The solution must be able to handle a large number of members, proposals, and votes efficiently.
*   **Scalability:** The solution must be scalable to handle a growing DAO membership.
*   **Thread-Safety:** The solution must be thread-safe and handle concurrent operations correctly.
*   **Code Quality:** The code must be well-structured, readable, and maintainable.

Good luck! You'll need it.
