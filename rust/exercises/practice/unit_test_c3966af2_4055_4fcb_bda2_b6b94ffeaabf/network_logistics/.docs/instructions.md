## Problem Title: Optimal Logistics Network Design

### Problem Description

You are tasked with designing an optimal logistics network for a rapidly growing e-commerce company. The company has a set of warehouses and a set of customer locations. Your goal is to determine the most cost-effective way to deliver goods from the warehouses to the customers, considering various constraints and factors.

The network consists of nodes (warehouses and customer locations) and edges (transportation routes). Each warehouse has a limited inventory capacity, and each customer location has a specific demand. The transportation routes have associated costs per unit of goods transported.

Your objective is to minimize the total transportation cost while satisfying customer demands and respecting warehouse capacities. However, due to the dynamic nature of the business, you also need to ensure the network is resilient to disruptions.

Specifically, you need to implement a function that takes the following inputs:

*   **Warehouses:** A vector of warehouse objects, each with an ID, location (x, y coordinates), and inventory capacity.
*   **Customers:** A vector of customer objects, each with an ID, location (x, y coordinates), and demand.
*   **Transportation Routes:** A vector of transportation route objects, each connecting two nodes (warehouse-customer, warehouse-warehouse, or customer-customer) with an associated cost per unit of goods. Assume that the transportation routes are bidirectional.
*   **Disruption Probability:** A probability (between 0 and 1) that any given transportation route might be disrupted (become unavailable).

Your function should output the following:

*   **Optimal Flow:** A data structure representing the optimal flow of goods through the network. It should indicate the amount of goods transported between each pair of connected nodes.
*   **Total Cost:** The total transportation cost associated with the optimal flow.
*   **Resilience Score:** A metric quantifying the network's resilience to disruptions. It should be calculated as the average percentage of customer demand satisfied after simulating multiple random disruptions.

**Constraints:**

*   All customer demands must be satisfied.
*   The total outflow from each warehouse cannot exceed its inventory capacity.
*   The flow along each transportation route must be non-negative.
*   The number of warehouses and customers can be large (up to 1000 each).
*   The number of transportation routes can be even larger (up to 100000).
*   The solution must be computationally efficient, especially for large networks.
*   The resilience score calculation should be accurate and efficient, requiring a sufficient number of simulations (at least 100) without taking excessively long time.

**Optimization Requirements:**

*   Minimize the total transportation cost.
*   Maximize the resilience score (implicitly, by choosing routes that provide redundancy).
*   Achieve a balance between cost and resilience. A solution with slightly higher cost but significantly improved resilience might be preferable.

**Edge Cases and Considerations:**

*   The network might be disconnected, making it impossible to satisfy all demands.
    Handle this gracefully and return an appropriate error.
*   There might be multiple optimal solutions with the same cost. Your solution should return one of them.
*   The disruption probability can significantly affect the optimal network design.

**Algorithmic Efficiency Requirements:**

*   The flow optimization algorithm should be efficient (e.g., a variant of the Ford-Fulkerson algorithm with Edmonds-Karp or Dinic's algorithm, or a more advanced linear programming solver).
*   The resilience score calculation should be optimized to minimize the number of flow recalculations needed for each simulation.

**Real-World Practical Scenarios:**

*   This problem models a real-world logistics network design challenge.
*   The resilience aspect is crucial for ensuring business continuity in the face of unexpected events (e.g., natural disasters, traffic congestion, or equipment failures).

**System Design Aspects:**

*   Consider the scalability of your solution to handle larger networks.
*   Think about how you would represent the network data structure efficiently.
*   Design your code to be modular and maintainable.
