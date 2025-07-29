## Project Name

```
Scalable Social Network Analytics
```

## Question Description

You are tasked with building a simplified, yet scalable, analytics module for a rapidly growing social network. The network consists of users and their connections (friendships). Your module needs to efficiently handle two primary types of queries:

1.  **Reachability Query:** Given two user IDs, determine if there is a path (direct or indirect) connecting them in the network.

2.  **Influence Score Query:** Given a user ID, calculate their "influence score." The influence score is defined as the number of users within a certain "degree of separation" from the given user.  A degree of separation of 'k' means you count all users reachable within k hops from the target user.

The social network is massive, with millions of users and connections, and the data is constantly evolving.  New users and connections are frequently added, and existing connections may be removed.

**Specific Requirements:**

*   **Data Structure:** Implement a data structure to represent the social network graph. You must choose an appropriate data structure considering both query performance and the frequency of updates (user/connection additions/removals). Consider space efficiency.

*   **Reachability Algorithm:** Implement an efficient algorithm to determine reachability between two users.  Consider the trade-offs between different graph traversal algorithms (e.g., BFS, DFS, Union-Find) in the context of this problem.

*   **Influence Score Algorithm:** Implement an efficient algorithm to calculate the influence score for a user, given a degree of separation `k`.

*   **Scalability:** Your solution should be scalable to handle a large number of users and connections.  Consider techniques like graph partitioning or distributed processing if needed (although for this problem, a single-machine solution with optimized data structures and algorithms is sufficient to pass, a note on how to scale out your design will be a plus).

*   **Efficiency:** Both reachability and influence score queries should be answered as quickly as possible. Optimize your algorithms for both time and space complexity.

*   **Dynamic Updates:**  Your data structure should support efficient addition and removal of users and connections.  These operations should not require rebuilding the entire data structure from scratch.  Consider how your choice of data structure impacts update performance.

*   **Memory Usage:** Memory consumption should be kept within reasonable limits. Unnecessary copying or redundant storage should be avoided.

**Input Format:**

Your program will receive a series of commands via standard input. Each command will be on a separate line. The commands are as follows:

*   `ADD_USER <user_id>`: Adds a user with the specified ID to the network.
*   `REMOVE_USER <user_id>`: Removes the user with the specified ID from the network. If the user does not exist, ignore the command.
*   `ADD_CONNECTION <user_id1> <user_id2>`: Adds a connection (friendship) between the two specified users.  The connection is undirected.
*   `REMOVE_CONNECTION <user_id1> <user_id2>`: Removes the connection between the two specified users. If the connection does not exist, ignore the command.
*   `ARE_REACHABLE <user_id1> <user_id2>`: Checks if the two specified users are reachable. Print "TRUE" to standard output if they are reachable, and "FALSE" otherwise.
*   `INFLUENCE_SCORE <user_id> <degree>`: Calculates the influence score for the specified user with the given degree of separation. Print the influence score (an integer) to standard output.

**Constraints:**

*   User IDs are integers in the range \[0, 1,000,000].
*   The number of users in the network will not exceed 1,000,000.
*   The number of connections in the network will not exceed 5,000,000.
*   The degree of separation `k` for the `INFLUENCE_SCORE` query will be in the range \[1, 10].
*   The number of commands will not exceed 100,000.
*   Commands are case-sensitive.
*   All commands will be valid according to the specified format.
*   Assume that the input is well formed and follows the rules, and that user ID will not exceed the upper bound.

**Example:**

```
ADD_USER 1
ADD_USER 2
ADD_USER 3
ADD_CONNECTION 1 2
ADD_CONNECTION 2 3
ARE_REACHABLE 1 3
INFLUENCE_SCORE 2 1
REMOVE_CONNECTION 2 3
ARE_REACHABLE 1 3
```

**Output for Example:**

```
TRUE
2
FALSE
```

**Grading:**

Your solution will be evaluated based on the following criteria:

*   **Correctness:** The accuracy of your reachability and influence score calculations.
*   **Efficiency:** The time and space complexity of your algorithms.  Solutions with lower complexity will receive higher scores.
*   **Scalability:**  The ability of your solution to handle large datasets.
*   **Code Quality:** The clarity, readability, and maintainability of your code.

This problem emphasizes a deep understanding of data structures, graph algorithms, and performance optimization techniques. Good luck!
