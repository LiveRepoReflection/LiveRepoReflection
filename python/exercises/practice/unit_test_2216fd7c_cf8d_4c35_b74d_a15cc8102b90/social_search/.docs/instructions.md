## Project Name

**Decentralized Social Graph Search**

## Question Description

Design and implement a distributed algorithm for efficiently searching a social graph stored across multiple nodes in a decentralized network.

**Scenario:** Imagine a new decentralized social network where user profiles and relationships (friendships, follows, etc.) are distributed across a peer-to-peer network. Each node in the network stores a subset of the overall social graph, including user profiles and their immediate connections. There is no central index or authority.

**Task:** Implement a function `search_social_graph(starting_node, search_query, max_hops, similarity_threshold)` that performs a distributed search of the social graph, starting from a given node, to find users whose profiles match a given search query.

**Input:**

*   `starting_node`:  A unique identifier for the node where the search originates. This node contains a subset of the social graph.
*   `search_query`: A string representing the search query.  This query is used to find users whose profiles contain relevant information.
*   `max_hops`: An integer representing the maximum number of "hops" (network traversals) the search can perform. This limits the scope of the search to prevent it from consuming excessive resources.  A hop constitutes traversing one edge in the social graph to reach a neighboring node.
*   `similarity_threshold`: A float between 0 and 1 representing the minimum similarity score required for a user profile to be considered a match for the search query. Use any reasonable string similarity metric (e.g., cosine similarity, Jaccard index) to compare the search query with user profile text.

**Constraints:**

*   **Decentralization:** The algorithm must operate without a central index or knowledge of the entire graph structure. Each node only knows about its directly connected neighbors.
*   **Efficiency:** Minimize network traffic and computational overhead.  Avoid unnecessary node visits and redundant computations.  Consider strategies to prevent cycles and repeated visits to the same node.
*   **Scalability:** The algorithm should be designed to handle a large social graph with many users and connections.
*   **Fault Tolerance:** The network may experience node failures or temporary unavailability. The algorithm should be reasonably resilient to such failures and continue to operate correctly when possible.
*   **Profile Similarity**: Each user profile is a string. The search result should return users whose profiles are "similar" to the search query. You will need to compute a "similarity score" between the user profile and the search query, and only return profiles with similarity scores higher than the `similarity_threshold`.
*   **Limited Resources**: Assume each node has limited computational resources and memory. Avoid storing excessive amounts of data during the search process.
*   **No Global Knowledge**: The algorithm must work without any global knowledge of the network topology or user distribution. Each node makes decisions based only on local information and communication with its neighbors.

**Output:**

A list of user IDs (strings) that match the search query, along with their corresponding similarity scores.  The list should be sorted in descending order of similarity score. The structure of the output should be `[(user_id_1, similarity_score_1), (user_id_2, similarity_score_2), ...]`.

**Data Structures:**

You can assume that each node in the network has access to the following data structures:

*   `node.user_profiles`: A dictionary where keys are user IDs (strings) and values are the user profiles (strings).
*   `node.neighbors`: A list of node IDs (strings) representing the node's direct neighbors in the social graph.
*   `node.get_user_profile(user_id)`: A method that returns the profile string for a given user ID, or `None` if the user is not found on that node.
*   `node.send_message(destination_node, message)`: A method to send a message to another node in the network. Messages can be arbitrary Python objects (e.g., dictionaries, lists).
*   `node.receive_message()`: A method to receive a message. This method should be non-blocking (i.e. return immediately). The return is the content of the message, or None if no message is waiting.

**Example (Illustrative):**

Let's say node "A" initiates the search with query "Python developer", `max_hops = 2`, and `similarity_threshold = 0.7`. The algorithm might traverse to node "B", then to node "C", searching user profiles along the way. If user "X" on node "B" has a profile that results in a similarity score of 0.8 with "Python developer", and user "Y" on node "C" has a similarity score of 0.75, and no other profiles match the threshold, the output would be:

`[("X", 0.8), ("Y", 0.75)]`

**Evaluation Criteria:**

*   **Correctness:** The algorithm must correctly identify users whose profiles match the search query within the specified `max_hops` and `similarity_threshold`.
*   **Efficiency:** The algorithm should minimize network traffic and computational overhead.
*   **Scalability:** The algorithm should be able to handle a large social graph.
*   **Fault Tolerance:** The algorithm should be resilient to node failures.
*   **Code Quality:** The code should be well-structured, documented, and easy to understand.

This problem requires a combination of graph traversal, distributed algorithms, text similarity calculation, and optimization techniques. Good luck!
