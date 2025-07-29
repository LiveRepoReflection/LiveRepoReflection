## The Quantum Entanglement Network

**Problem Description:**

A groundbreaking quantum communication network is being developed, aiming to connect various research labs across the globe. This network leverages the principles of quantum entanglement to ensure secure and instantaneous data transfer. Each lab represents a node in the network.

The network has a central hub responsible for managing the quantum entanglement pairs. Each entanglement pair links two distinct labs. However, due to the delicate nature of quantum entanglement, not all labs can be directly linked. Furthermore, the entanglement process has an associated "fragility score," representing the susceptibility of the link to environmental disturbances. A higher fragility score indicates a less stable connection.

The goal is to design an algorithm that efficiently determines the **most resilient connected component** within the network. A connected component is a subset of labs that can communicate with each other, directly or indirectly, via entanglement links. The resilience of a connected component is defined as the **minimum fragility score** among all entanglement links within that component. The most resilient connected component is the one with the highest minimum fragility score.

Your task is to write a function that takes as input:

1.  `num_labs`: The total number of research labs in the network (numbered from 0 to `num_labs - 1`).
2.  `entanglement_links`: A list of tuples, where each tuple `(lab1, lab2, fragility)` represents an entanglement link between `lab1` and `lab2` with the given `fragility` score.

The function should return the resilience score of the most resilient connected component in the network. If the network is empty (no labs or links), return 0. If no connected component exists (isolated labs and no links), return 0.

**Constraints and Edge Cases:**

*   `1 <= num_labs <= 10^5`
*   `0 <= fragility <= 10^9`
*   The number of `entanglement_links` can be up to `2 * 10^5`.
*   There can be multiple connected components in the network.
*   A lab can be part of at most one connected component.
*   The graph represented by the entanglement links is undirected.
*   Labs are numbered from 0 to `num_labs - 1`.
*   Input should be validated.
*   The algorithm should be efficient enough to handle the maximum input size within a reasonable time limit (e.g., a few seconds).
* Consider the edge case where a link connects a lab to itself, and handle it appropriately.
* The problem must be solved using Python.

**Optimization Requirements:**

The solution should be optimized for both time and space complexity. Brute-force approaches will likely not pass the test cases within the time limit. Consider using appropriate data structures and algorithms to achieve optimal performance.

**Multiple Valid Approaches:**

There are several valid approaches to solve this problem, including variations of graph traversal algorithms (e.g., Depth-First Search, Breadth-First Search) combined with techniques for finding the minimum value within a component. Different approaches may have different trade-offs in terms of time and space complexity.

**Real-World Practical Scenarios:**

This problem mirrors the challenges encountered in designing and maintaining real-world communication networks, where link reliability and network resilience are critical factors. It touches on aspects of network topology, fault tolerance, and resource optimization.
