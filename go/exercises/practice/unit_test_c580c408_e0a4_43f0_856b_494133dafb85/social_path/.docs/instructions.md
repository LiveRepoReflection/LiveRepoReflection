## Question: Decentralized Social Network Pathfinding

### Question Description

You are tasked with building a pathfinding service for a decentralized social network. Unlike traditional social networks with a central server and database, this network is built on a peer-to-peer architecture. Each user node maintains a local graph of their direct connections (friends) and some known connections of their friends (friends of friends, etc.), up to a limited depth. Due to the decentralized nature, the complete network graph is unknown, and communication between nodes is subject to latency and potential failures.

Given a starting user ID, a target user ID, and a maximum path length, your service must find the shortest path between the two users within the decentralized network.  The path must not exceed the maximum path length. Due to the limitations of the decentralized network, you can only explore the network through iterative queries to individual user nodes, retrieving their local connection graphs.

**Input:**

*   `startUserID`: The ID of the user where the pathfinding starts (string).
*   `targetUserID`: The ID of the user we are trying to reach (string).
*   `maxPathLength`: The maximum number of hops allowed in the path (integer, >= 1).  A path exceeding this length is considered invalid.
*   `userNode`: An interface (or a function adhering to a specific signature) that allows querying a user node for its local connection graph. The `userNode` accepts a userID `string` and returns a `map[string][]string`, representing the local graph of that user. The keys of the map are user IDs, and the values are lists of user IDs that the key user is directly connected to. If a user ID doesn't exist the userNode must return an empty `map[string][]string{}`. Assume that calling userNode is computationally expensive, and should be minimized.
    ```go
    // Example:
    func userNode(userID string) map[string][]string {
        // Implementation to retrieve user's connection graph
        // from the decentralized network.
        // Returns an empty map if user not found.
    }
    ```

**Output:**

*   A list of user IDs representing the shortest path from `startUserID` to `targetUserID`.  If no path is found within the `maxPathLength`, return an empty list.
*   If a path is found, the first element of the list must be `startUserID`, and the last element must be `targetUserID`.
*   If multiple shortest paths exist, return any one of them.

**Constraints:**

*   The network can be very large, but each individual user's local graph is relatively small (e.g., hundreds or thousands of connections).
*   The `userNode` function (or interface method) is the **only** way to access the network's structure. Direct access to a global graph is not allowed.
*   The `userNode` calls are potentially slow and may fail (return empty graph). You should design your algorithm to be resilient to such issues and attempt to minimize the number of `userNode` calls.
*   The solution must be efficient in terms of both time and memory usage.  Excessive memory consumption might lead to program termination.
*   The network graph may contain cycles.
*   User IDs are unique strings.

**Example:**

```go
// Assume the following network structure is known through userNode calls:
// userNode("A") returns: {"A": ["B", "C"]}
// userNode("B") returns: {"B": ["A", "D", "E"]}
// userNode("C") returns: {"C": ["A", "F"]}
// userNode("D") returns: {"D": ["B"]}
// userNode("E") returns: {"E": ["B"]}
// userNode("F") returns: {"F": ["C"]}

startUserID := "A"
targetUserID := "D"
maxPathLength := 3

// A possible valid output: ["A", "B", "D"]

startUserID = "A"
targetUserID = "F"
maxPathLength = 2
// A possible valid output: ["A", "C", "F"]

startUserID = "A"
targetUserID = "G" // User "G" does not exist or is not reachable within maxPathLength
maxPathLength = 3

// Output: []

startUserID = "A"
targetUserID = "A"
maxPathLength = 3

// Output: []  (No Path when start equals target)
```

**Challenge:**

Design an algorithm that efficiently explores the decentralized network, finds the shortest path (if one exists), and minimizes the number of calls to the `userNode` function while adhering to the `maxPathLength` constraint.  Consider the trade-offs between different search strategies (e.g., Breadth-First Search, Depth-First Search, A\*). Implement your solution in Go, paying close attention to performance and error handling.
