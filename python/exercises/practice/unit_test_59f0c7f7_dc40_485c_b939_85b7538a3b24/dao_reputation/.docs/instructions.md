## Problem: Decentralized Autonomous Organization (DAO) Reputation System

### Question Description

You are tasked with designing and implementing a reputation system for a Decentralized Autonomous Organization (DAO). This DAO allows members to propose and vote on projects. A member's reputation within the DAO influences their voting power and their ability to successfully propose projects. The goal is to create a robust and scalable reputation system that accurately reflects a member's contribution and trustworthiness within the DAO, while being resistant to manipulation.

The DAO has a large number of members (potentially millions) and a high volume of proposals and votes occurring concurrently. The reputation system must efficiently handle these concurrent operations.

Each member starts with a base reputation score. Reputation can be earned or lost based on several factors:

1.  **Proposal Success:** When a member's proposed project is successfully voted and implemented, their reputation increases. The increase is proportional to the project's impact (measured in tokens earned by the DAO) and inversely proportional to the number of co-proposers.

2.  **Voting Accuracy:** Members gain reputation by voting in line with the final outcome of a successful project. The reputation gain is higher for projects with closer vote margins. Conversely, voting against a successful project reduces reputation. The magnitude of the reputation change depends on the voting margin.

3.  **Staking:** Members can stake DAO tokens to further boost their reputation. The reputation boost is a logarithmic function of the amount of staked tokens.

4.  **Reporting Malicious Activity:** Members can report other members for malicious activity (e.g., spam proposals, Sybil attacks). If a report is validated by a DAO-appointed moderator, the reported member's reputation decreases significantly, and the reporting member's reputation increases moderately. False reports result in a reputation decrease for the reporter.

5. **Time Decay:** Reputation naturally decays over time to reflect the fact that past contributions become less relevant.

You need to implement the following functionalities:

*   **`update_reputation(member_id, reputation_change)`:** Updates a member's reputation score. This function should be thread-safe, handling concurrent reputation updates.

*   **`get_reputation(member_id)`:** Retrieves a member's current reputation score. This function should have minimal latency, even during periods of high concurrent updates.

*   **`handle_proposal_success(proposer_id, project_impact, co_proposers)`:** Calculates and applies the reputation gain for a proposer based on the project's success.

*   **`handle_vote(member_id, proposal_id, vote, project_success, voting_margin)`:** Calculates and applies the reputation change for a voter based on their vote and the project's outcome.

*   **`handle_staking(member_id, staked_amount)`:** Updates a member's reputation based on their staked tokens.

*   **`handle_report(reporter_id, reported_id, is_valid)`:** Calculates and applies reputation changes for both the reporter and the reported member, based on the validity of the report.

*   **`apply_time_decay()`:** Applies a time decay factor to all member reputations. This function should be efficient and avoid locking the entire reputation data structure.

**Constraints:**

*   **Scalability:** The system must handle millions of members and a high volume of concurrent transactions.
*   **Concurrency:** All reputation updates must be thread-safe.
*   **Low Latency:** Reputation retrieval must be fast, even during periods of high activity.
*   **Data Persistence:** Reputation data must be persisted to disk. Consider using a suitable database or data storage solution.
*   **Attack Resistance:** The system should be designed to be resistant to reputation manipulation and Sybil attacks. (While you don't need to implement full Sybil resistance, your design should consider these vulnerabilities.)
*   **Realistic Reputation Range:** Reputation should be bounded within a reasonable range (e.g., 0 to 1000).

**Bonus:**

*   Implement a mechanism for weighting votes based on reputation.
*   Implement a reputation delegation system, where members can delegate their reputation to other members for specific projects or domains.
*   Implement a monitoring system to detect suspicious reputation changes.

**Note:** You are not expected to implement a full DAO. Focus on the design and implementation of the reputation system itself. You are free to use any suitable libraries and frameworks. Provide a clear explanation of your design choices and the rationale behind them. Explain how you addressed the constraints and potential vulnerabilities.
