## Question: Optimal Edge Router Configuration

### Question Description

You are tasked with designing and implementing an algorithm to configure a network of edge routers in a distributed content delivery network (CDN). The CDN consists of a set of edge routers strategically located around the globe. Your goal is to minimize the average latency experienced by users accessing content served by the CDN.

The CDN has a central content repository and a set of `N` edge routers. Each edge router has a limited storage capacity and serves content to users within its geographical region.

**Input:**

1.  **Edge Router Locations:** A list of `N` edge router locations, represented as (latitude, longitude) coordinates.
2.  **User Request Distribution:** A list of `M` user request locations, also represented as (latitude, longitude) coordinates, along with the frequency of requests originating from each location.
3.  **Content Popularity:** A list of `K` content items, each with a size (in MB) and a popularity score (number of requests per unit time).
4.  **Edge Router Capacity:** Each edge router has a maximum storage capacity `C` (in MB).
5.  **Network Latency Matrix:** A matrix representing the network latency (in milliseconds) between each pair of locations (edge routers and the central content repository). The central content repository is considered location 0, and the edge routers are locations 1 to N.

**Constraints:**

*   `1 <= N <= 50` (Number of Edge Routers)
*   `1 <= M <= 1000` (Number of User Request Locations)
*   `1 <= K <= 200` (Number of Content Items)
*   `1 <= C <= 10000` (Edge Router Capacity in MB)
*   Content sizes and popularity scores are positive integers.
*   Latencies are non-negative integers.

**Objective:**

Determine the optimal content placement strategy for each edge router to minimize the average user latency. The content placement strategy involves deciding which of the `K` content items to store on each of the `N` edge routers, subject to the capacity constraint `C`. Each content item can be stored on multiple edge routers.

**Latency Calculation:**

The latency experienced by a user request is determined as follows:

1.  Find the closest edge router to the user's location (using Euclidean distance).
2.  If the requested content item is available on the closest edge router, the latency is the network latency between the edge router and the user's location.
3.  If the requested content item is *not* available on the closest edge router, the content must be fetched from the central content repository. In this case, the latency is the sum of:
    *   The network latency between the edge router and the user's location.
    *   The network latency between the central content repository and the closest edge router.

**Output:**

A data structure (e.g., a list of sets) representing the content placement strategy for each edge router. Specifically, the output should be a list of `N` sets, where the i-th set contains the indices (0-indexed) of the content items stored on the i-th edge router.

**Evaluation:**

Your solution will be evaluated based on the average latency achieved across all user requests. The lower the average latency, the better. The evaluation will be performed on hidden test cases with varying input parameters.

**Optimization Requirements:**

*   Your solution must be efficient enough to handle the given constraints within a reasonable time limit (e.g., a few minutes).
*   Consider using appropriate data structures and algorithms to optimize the content placement strategy. Dynamic programming or other optimization techniques may be helpful.
*   Solutions that produce significantly better average latency scores will be ranked higher.

**Example:**

Let's say you have two edge routers (N=2), two user request locations (M=2) and two content items (K=2). Assume the content placement strategy is such that Edge Router 1 stores Content Item 0, and Edge Router 2 stores Content Item 1. The algorithm will calculate the latency for each request coming from each User Request Location, taking into consideration the proximity of the Edge Routers, the content placement and the Network Latency Matrix. It will sum up all the latencies and calculate the average latency.

This problem requires a good understanding of network optimization, content delivery, and algorithmic problem-solving. Good luck!
