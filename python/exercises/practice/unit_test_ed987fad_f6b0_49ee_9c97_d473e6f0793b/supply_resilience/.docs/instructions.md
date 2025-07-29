Okay, here's a challenging problem description designed for a high-level programming competition:

**Problem Title:** Optimal Supply Chain Resiliency

**Problem Description:**

A global company, "OmniCorp," operates a complex supply chain represented as a directed acyclic graph (DAG). Each node in the graph represents a facility (e.g., manufacturing plant, warehouse, distribution center) and each directed edge represents the flow of goods between facilities. Each facility has a processing capacity, and each edge has a maximum flow capacity.

Due to increasing geopolitical instability, OmniCorp needs to enhance the resiliency of its supply chain. Resiliency is defined as the ability to maintain a minimum level of output delivery to customers (represented as a set of sink nodes in the DAG) even when some facilities are disrupted (become non-operational).

The company has a limited budget to harden facilities against disruption. Hardening a facility reduces its probability of disruption. Each facility has a "hardening cost" associated with it, and a "disruption probability" if *not* hardened. If hardened, the disruption probability becomes zero.

The company also has the option to establish redundant supply routes. For any two existing adjacent facilities A and B in the original supply chain network, the network architect can invest to build a redundant supply route between A and B with the same flow capacity as the original link between A and B.

Your task is to design an algorithm that determines the optimal set of facilities to harden and the optimal set of redundant routes to construct, within the given budget, to maximize the *minimum expected delivery* to customers under various disruption scenarios.

**Input:**

*   A directed acyclic graph (DAG) represented as a list of nodes and a list of edges.
    *   Each node has:
        *   `id`: Unique identifier.
        *   `capacity`: Processing capacity.
        *   `hardening_cost`: Cost to harden the facility.
        *   `disruption_probability`: Probability of disruption if *not* hardened.
        *   `is_customer`: Boolean indicating if this is a customer node (sink).
    *   Each edge has:
        *   `source`: Source node `id`.
        *   `target`: Target node `id`.
        *   `capacity`: Maximum flow capacity.
*   `budget`: The total budget available for hardening facilities and constructing redundant supply routes.
*   `number_of_scenarios`: The number of disruption scenarios to simulate.

**Output:**

*   A tuple containing:
    *   A set of facility `id`s to harden.
    *   A set of tuples `(source_id, target_id)` representing redundant routes to construct.
    *   The expected minimum delivery amount to customers.

**Constraints:**

*   The number of nodes in the graph can be up to 200.
*   The number of edges in the graph can be up to 500.
*   The budget can be up to 10,000.
*   The number of scenarios can be up to 100.
*   The disruption probability for each facility is between 0.0 and 1.0.
*   The hardening cost for each facility is a positive integer.
*   You must maximize the *minimum* expected delivery to customer nodes across all simulated disruption scenarios, where the total cost of hardening and route construction is within the budget.
*   The runtime of your solution is limited to 60 seconds.

**Scoring:**

The score will be based on the difference between the expected minimum delivery amount to customers achieved by your solution and the expected minimum delivery of the baseline solution. Solutions that violate the budget constraint will receive a score of zero. Solutions that do not complete within the time limit will receive a score of zero.

**Notes:**

*   A disruption scenario is a random realization of facilities being operational or non-operational based on their disruption probabilities (after hardening).
*   The "delivery" to a customer node is the amount of flow that reaches that node from the source nodes (nodes with no incoming edges) of the DAG.
*   You must determine the maximum flow from source nodes to customer nodes in each disruption scenario, considering facility and edge capacities. Standard max flow algorithms (e.g., Ford-Fulkerson, Edmonds-Karp, Dinic's) can be used.
*   Efficiently exploring the solution space (which facilities to harden, which edges to make redundant) is crucial for achieving a high score. Consider using heuristics, approximation algorithms, or metaheuristic optimization techniques (e.g., simulated annealing, genetic algorithms) to find a near-optimal solution within the time limit.
