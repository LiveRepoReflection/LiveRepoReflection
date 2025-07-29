## Problem: Decentralized Social Network Analysis

**Description:**

You are tasked with building an analytical engine for a new decentralized social network, "Nexus." Unlike traditional social networks with centralized servers, Nexus stores user data across a distributed peer-to-peer network. Each user's profile, connections (friends), and posts are stored on a subset of nodes in the network. Due to the distributed nature, data retrieval is inherently complex and resource-intensive.

Your engine needs to perform complex social network analysis operations on Nexus data. Specifically, you need to efficiently calculate the *k-core decomposition* of the network. The k-core of a graph is the largest subgraph in which each vertex has degree at least *k*. The k-core decomposition involves finding the maximal k-core for every possible value of *k*.

**Input:**

You will receive two types of input:

1.  **Network Metadata:** A stream of data describing the Nexus network. Each line represents a user node and its immediate connections. The format is:

    `userID: friend1,friend2,friend3,...`

    Where `userID` and `friend1, friend2,...` are all unique integer identifiers. This stream may be very large (gigabytes) and cannot be fully loaded into memory. The order of user IDs and their friends isn't guaranteed. Duplicate friend relations won't exist in input.

2.  **Query:** A single integer, *k*, representing the coreness value you need to determine the members of.

**Output:**

A sorted list of userIDs that are members of the k-core of the Nexus network described by the input stream. The list must be sorted in ascending order. Output the list to standard output, one userID per line.

**Constraints:**

*   **Memory Limit:** Your solution must use a limited amount of memory. You can assume you have significantly less memory than the total size of the network metadata. Aim for a memory footprint that grows sub-linearly with the number of nodes.
*   **Scalability:** Your solution must be able to handle networks with millions of users and connections.
*   **Efficiency:** The time complexity of your solution is critical. A naive approach of loading the entire graph into memory will not work within the memory constraints.
*   **Distribution:** You cannot assume all node data is readily available. You must design an algorithm that can efficiently process the data as it streams in, without requiring random access or complete graph reconstruction.
*   *   `0 <= k <= N` where `N` is the total number of users in the network.
*   UserIDs will be positive integers.
*   You can assume the input data is well-formed (e.g., no malformed lines, non-integer IDs, etc.).
*   No of users `N` can be up to `10^6`
*   No of friends a user can have `F` can be up to `10^3`

**Example:**

**Input (Network Metadata):**

```
1:2,3,4
2:1,3,5
3:1,2,4,6
4:1,3,6
5:2
6:3,4,7
7:6
```

**Input (Query):**

```
2
```

**Output:**

```
1
2
3
4
6
```

**Explanation:**

1.  The original graph has the nodes {1, 2, 3, 4, 5, 6, 7}.
2.  The 1-core (all nodes with degree at least 1) is {1, 2, 3, 4, 6, 5, 7} (remove none).
3.  The 2-core (all nodes with degree at least 2) is {1, 2, 3, 4, 6} (remove 5 and 7). All nodes in this subgraph have degree at least 2.

**Challenge:**

Develop a Go program that efficiently computes the k-core decomposition for the Nexus social network, given the streaming network metadata and the query coreness value, while adhering to the memory and scalability constraints.  Consider using techniques like streaming algorithms, external memory algorithms, or approximation algorithms to address the challenges.
