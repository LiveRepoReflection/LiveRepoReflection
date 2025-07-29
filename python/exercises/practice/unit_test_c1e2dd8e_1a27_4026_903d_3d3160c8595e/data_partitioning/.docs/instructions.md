## Problem: Optimal Network Partitioning for Data Localization

**Question Description:**

You are tasked with designing a network architecture for a multinational corporation that needs to comply with stringent data localization regulations. The corporation has data centers distributed across the globe. Each data center stores specific types of data, and certain countries mandate that specific data types must reside within their borders.

Your goal is to determine the *minimum number of network partitions* required to satisfy all data localization requirements.

**Formal Definition:**

You are given:

1.  **Data Centers (Nodes):** A list of data center locations (e.g., "USA", "Germany", "China"). Represented as nodes in a graph.
2.  **Data Types:** A list of data types (e.g., "Financial", "Personal", "Operational").
3.  **Data Residency Requirements:** A set of rules specifying which data types must reside in which countries.  These rules are expressed as tuples: `(data_type, country)`. For example, `("Personal", "Germany")` means that "Personal" data must reside in "Germany".
4.  **Network Connectivity (Edges):** A list of connections between data centers.  Each connection represents a bidirectional communication link. Represented as edges in a graph.
5.  **Data Storage Mapping:**  A mapping indicating which data types are stored in each data center. This is expressed as tuples: `(data_center, data_type)`. For example, `("USA", "Financial")` means the "USA" data center stores "Financial" data.

A *network partition* is the removal of one or more edges from the network graph. The number of network partitions is the count of edges removed. Partitioning the network isolates groups of data centers.

Your solution must determine the *minimum* number of network partitions required to ensure that all data residency requirements are satisfied. In other words, you want to minimize the number of communication links you sever. The number of data centers and data types are limited to 200 each.

**Constraints:**

*   **Minimality:** Your solution must find the *absolute minimum* number of partitions.
*   **Completeness:** All data residency requirements *must* be satisfied after partitioning.
*   **Efficiency:**  The algorithm must be efficient enough to handle up to 200 data centers, 200 data types, and a dense network (i.e., many connections between data centers).  Brute-force approaches that explore all possible partition combinations will not scale and are unacceptable.
*   **Implicit Edge Case:** If a data center in country A contains data that *must* reside in country B, and there is a direct connection between A and B, then that connection *must* be severed. If there is NO connection between A and B, then the fact that the data needs to be moved does *not* constitute a need for a partition.
*   **Complex Data Dependencies:** A single data center can store multiple data types, and a single data type can be stored in multiple data centers.
*   **No Data Duplication:**  The data cannot be duplicated. If a data type must reside in a specific country, all instances of that data type must be moved to data centers within that country.
*   **Data Movement is Allowed**: After partitioning, it is assumed that all the data of required types will be moved to its destined data center. The only goal is to find the minimum number of partitions needed to make the data movement regulation-compliant.

**Input Format:**

The input will be provided in a structured format (e.g., JSON, text file). You should clearly define the input format you expect.

**Output Format:**

The output should be a single integer representing the minimum number of network partitions required.

**Example Scenario:**

(This is a simplified example; a full test case would be much larger.)

*   Data Centers: `["USA", "Germany", "China"]`
*   Data Types: `["Financial", "Personal"]`
*   Data Residency Requirements: `[("Personal", "Germany")]`
*   Network Connectivity: `[("USA", "Germany"), ("Germany", "China")]`
*   Data Storage Mapping: `[("USA", "Personal"), ("China", "Financial")]`

In this scenario, the "USA" data center stores "Personal" data, which must reside in "Germany".  Therefore, the connection between "USA" and "Germany" must be severed. The output is 1.

**Grading Criteria:**

*   Correctness: The algorithm must correctly determine the minimum number of partitions for all valid input cases.
*   Efficiency: The algorithm must be efficient enough to handle large datasets.
*   Clarity: The code must be well-structured and easy to understand.
*   Scalability: The approach should be able to handle increasing the number of data centers, data types and dependencies.

This problem requires a combination of graph algorithms, constraint satisfaction techniques, and optimization strategies. A well-designed solution will likely involve a clever application of min-cut/max-flow algorithms or other network flow techniques. Good luck!
