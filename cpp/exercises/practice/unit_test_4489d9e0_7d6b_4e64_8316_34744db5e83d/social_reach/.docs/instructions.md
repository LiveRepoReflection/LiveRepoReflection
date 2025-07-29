## Problem: Decentralized Social Network Analysis

### Question Description

You are tasked with building an analytical tool for a decentralized social network. This network is structured as a peer-to-peer system where users (nodes) directly maintain connections (edges) with other users they follow. Due to the decentralized nature, there's no central authority or global knowledge of the entire network structure.

Each user node only has information about:

1.  **Its own ID:** A unique integer identifier.
2.  **Its direct followers:** A list of user IDs that follow this user.
3.  **Its direct followees:** A list of user IDs that this user follows.
4.  **Content Posted:** A list of strings the user posted to the network.

You need to implement a distributed algorithm to calculate the **k-hop reachability** for a given user in the network.

**k-hop reachability** for a user *U* is defined as the set of all users that can be reached from user *U* within *k* hops (i.e., traversing at most *k* edges).

**Input:**

*   `startingUserID`: The ID of the user for whom to calculate reachability.
*   `k`: The maximum number of hops to consider.
*   `networkData`: A function that, given a `userID`, returns a tuple containing:
    *   `followers`: A `std::vector<int>` representing the IDs of users following `userID`.
    *   `followees`: A `std::vector<int>` representing the IDs of users that `userID` follows.
    *   `content`: A `std::vector<std::string>` representing the content posted by the user.

**Output:**

*   A `std::set<int>` containing the IDs of all users reachable from `startingUserID` within `k` hops (including the `startingUserID` itself). The set should be sorted in ascending order.

**Constraints and Considerations:**

1.  **Decentralized Data:** You can only access the network information through the provided `networkData` function. You cannot assume to have a global view of the network. The function call is expensive, try to minimize calls as much as possible.
2.  **Large Network:** The network can be very large (millions of users). Your solution needs to be efficient in terms of both time and memory. Avoid unnecessary data duplication or computations.
3.  **Cycles:** The network may contain cycles. Your algorithm should handle cycles correctly and avoid infinite loops.
4.  **Optimization:** The `networkData` function is assumed to have an API call limit. Your solution should minimize the number of calls to the `networkData` function to stay within the API limits during evaluation. Solutions that require excessive function calls will be penalized or may timeout.
5.  **No External Libraries:** You are restricted to using standard C++ libraries (STL).  No external libraries (e.g., Boost Graph Library) are allowed.
6.  **Error Handling:** The `networkData` function is guaranteed to return valid data for any user ID that exists in the network. You do not need to handle cases where the function returns an error or invalid data.

**Example:**

Assume the following simplified network structure (represented conceptually, not how your code receives data):

*   User 1 follows User 2 and User 3.
*   User 2 follows User 4.
*   User 3 follows User 5.
*   User 4 follows User 1.

If `startingUserID` is 1 and `k` is 2, the expected output is `{1, 2, 3, 4, 5}`.  User 1 can reach users 2 and 3 in 1 hop. It can reach user 4 (via user 2) and user 5 (via user 3) in 2 hops. User 1 can also reach user 1 via user 2-> user 4, and user 3 -> user 5.

**Challenge:**

The primary challenge lies in efficiently exploring the network without knowing its global structure, while minimizing calls to the `networkData` function and handling cycles correctly within the given memory and time constraints.  The optimization requirement of minimizing `networkData` function calls is crucial for passing all test cases.
