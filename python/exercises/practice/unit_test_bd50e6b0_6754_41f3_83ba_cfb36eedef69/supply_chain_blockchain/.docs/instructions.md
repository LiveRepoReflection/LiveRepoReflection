## Problem: Decentralized Supply Chain Optimization

**Description:**

You are tasked with designing an optimized supply chain network for a globally distributed manufacturing company using a blockchain to ensure transparency and immutability. The company produces a complex product assembled from numerous components sourced from various suppliers and processed in different factories before final assembly and distribution.

**Details:**

1.  **Network Representation:** The supply chain is represented as a directed acyclic graph (DAG). Each node in the graph represents a location (supplier, factory, distribution center). Each edge represents the flow of materials or products between locations. Edges have associated costs (transportation, processing) and time delays. Each node has a capacity for processing or storing materials.

2.  **Blockchain Integration:** Critical transactions (orders, shipments, quality control results, payments) are recorded on a permissioned blockchain. This ensures traceability and prevents tampering. You are given a function `record_transaction(data)` that simulates recording data on the blockchain. This function is atomic and thread-safe.

3.  **Demand Forecasting:** The demand for the final product fluctuates over time. You are given a function `get_demand(time)` that returns the demand at a specific time.

4.  **Optimization Goal:** Minimize the total cost of fulfilling customer demand over a given time horizon while adhering to capacity constraints and time delays. The cost includes transportation, processing, and penalties for unmet demand.

5.  **Decentralized Decision Making:** Each node in the supply chain is an independent entity that can make local decisions (e.g., order quantity, production schedule) based on its own information and incentives. However, these decisions must be coordinated to achieve global optimization.

6.  **Constraints:**
    *   Node capacities must not be exceeded.
    *   Materials must arrive at a node before they can be processed.
    *   The blockchain must be used to record all significant transactions.
    *   You are given the locations, their capacities and products they can process.

**Input:**

*   A DAG representing the supply chain network (nodes, edges, costs, delays, capacities).
*   A time horizon `T`.
*   A function `get_demand(time)` that returns the demand at a given time.
*   A function `record_transaction(data)` to record data on the blockchain.
*   A set of locations, their processing capacities and a list of products they are capable of processing.

**Output:**

*   A schedule of material flows and production activities for each node in the supply chain over the time horizon `T`. The schedule should specify:
    *   The quantity of each component ordered from each supplier at each time.
    *   The quantity of each component processed at each factory at each time.
    *   The quantity of the final product shipped from the final assembly location to the distribution center at each time.
*   The total cost of the schedule.

**Evaluation Criteria:**

*   Correctness: The schedule must satisfy all constraints and fulfill customer demand as much as possible.
*   Cost: The schedule must minimize the total cost of fulfilling customer demand.
*   Efficiency: The solution must be computationally efficient, especially for large supply chain networks and long time horizons.
*   Scalability: The solution should be able to handle dynamic changes in the supply chain network (e.g., new suppliers, factory shutdowns).
*   Blockchain Integration: Proper use of the `record_transaction` function to ensure traceability.

**Bonus:**

*   Implement a mechanism for handling unexpected events (e.g., supplier delays, factory breakdowns) and dynamically adjusting the schedule.
*   Incorporate quality control data from the blockchain into the decision-making process.
*   Design a system that incentivizes nodes to cooperate and share information to improve overall supply chain performance.

This problem requires a combination of graph algorithms, optimization techniques (e.g., linear programming, dynamic programming), distributed systems concepts, and blockchain knowledge. It also demands careful consideration of edge cases and performance optimization. Good luck!
