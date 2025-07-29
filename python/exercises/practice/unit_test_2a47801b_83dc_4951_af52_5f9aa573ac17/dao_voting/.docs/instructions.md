## Problem: Decentralized Autonomous Organization (DAO) Voting Simulation with Reputation and Sybil Resistance

**Description:**

You are tasked with building a simulation of a voting system within a Decentralized Autonomous Organization (DAO). This DAO utilizes a reputation system to weight votes and aims to mitigate Sybil attacks (where a single entity creates numerous fake accounts to disproportionately influence the outcome).

The DAO has a membership of `N` participants, each identified by a unique integer ID from `0` to `N-1`. Each participant has a reputation score, which is a non-negative integer. Participants vote on proposals by submitting a signed transaction including their ID and their YES or NO vote.

Your task is to implement a system to simulate the process of collecting votes, verifying signatures, calculating the weighted vote count (based on reputation), and determining the outcome of a proposal. The system must incorporate a Sybil resistance mechanism to prevent malicious actors from creating numerous accounts to manipulate the vote.

**Specific Requirements:**

1.  **Participant Class:**
    *   Each participant has a unique ID, a reputation score, a private key, and a public key.
    *   Implement a method to sign votes using their private key. The vote should include the proposal ID, the voter's ID, and the voter's decision (YES or NO). You are free to choose appropriate signing algorithm.

2.  **Reputation System:**
    *   Reputation is a non-negative integer.
    *   The weight of a participant's vote is proportional to their reputation score.

3.  **Vote Aggregation:**
    *   Implement a mechanism to collect votes for a specific proposal.
    *   The system must verify the signature of each vote using the corresponding public key.  Invalid signatures should be rejected.
    *   Calculate the total weighted "YES" votes and the total weighted "NO" votes.

4.  **Sybil Resistance (Quadratic Voting Adaptation):**
    *   To mitigate Sybil attacks, implement a modified form of quadratic voting.  Instead of directly summing reputation scores, apply a square root function to each participant's reputation before weighting their vote.  That is, the effective weight of a participant's vote is `sqrt(reputation)`.
    *   This makes it significantly more difficult to gain influence by creating many low-reputation accounts.

5.  **Proposal Outcome Determination:**
    *   A proposal passes if the total weighted "YES" votes are strictly greater than the total weighted "NO" votes. If they are equal or "NO" votes are strictly greater than "YES" votes, the proposal fails.

6.  **Input Constraints and Edge Cases:**
    *   The number of participants `N` can be large (up to 10,000).
    *   Reputation scores can range from 0 to 1,000,000.
    *   The system must handle invalid signatures, duplicate votes from the same participant (only the first vote counts), and participants with zero reputation.

7. **Performance Considerations:**
    *   The vote aggregation process should be optimized for efficiency.  Consider the time complexity of signature verification and weighted vote calculation, especially when dealing with a large number of participants.

**Input:**

*   A list of participants, each represented as a tuple: `(participant_id, reputation_score, public_key, private_key)`.
*   A list of votes, each represented as a tuple: `(proposal_id, voter_id, vote_decision, signature)`. Vote decision can be either `YES` or `NO`.

**Output:**

*   A boolean value indicating whether the proposal passes (True) or fails (False).

**Example:** (Illustrative; you'll need to generate keys and signatures for a real test)

```python
participants = [
    (0, 100, "public_key_0", "private_key_0"), # Public and private keys are placeholder
    (1, 225, "public_key_1", "private_key_1"),
    (2, 400, "public_key_2", "private_key_2"),
]

votes = [
    (1, 0, "YES", "signature_0"), # Proposal ID = 1, Voter ID = 0, Decision = YES
    (1, 1, "YES", "signature_1"),
    (1, 2, "NO", "signature_2"),
]

outcome = determine_proposal_outcome(participants, votes, 1)

print(outcome)  # Expected output: True (depending on the signatures)
```

**Evaluation Criteria:**

*   Correctness: The system accurately determines the proposal outcome based on the given inputs and constraints.
*   Sybil Resistance: The quadratic voting mechanism effectively mitigates the impact of Sybil attacks.
*   Efficiency: The vote aggregation process is optimized for performance, especially with a large number of participants.
*   Code Quality: The code is well-structured, readable, and maintainable.
*   Security: The signature verification process is robust and prevents unauthorized vote manipulation.

This problem requires a solid understanding of data structures, algorithms, basic cryptography (signing and verification), and system design principles. Good luck!
