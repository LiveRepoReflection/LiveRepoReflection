Okay, here's a challenging Go coding problem designed to test advanced skills and algorithmic thinking.

### Project Name

```
network-optimizer
```

### Question Description

You are designing a content delivery network (CDN) to efficiently serve video content to users across the globe. The CDN consists of a set of servers connected by network links. Each server stores a subset of the available video files. When a user requests a video, the CDN needs to find the optimal path to serve the video from a server that has it stored.

**Input:**

*   `servers`: A list of server nodes, represented as integers (e.g., `[]int{1, 2, 3}`).  Each server has a unique ID.
*   `videos`: A list of video files, represented as strings (e.g., `[]string{"video1.mp4", "video2.mp4"}`). Each video has a unique name.
*   `storage`: A map where the key is a server ID (integer), and the value is a list of video names (strings) stored on that server.  (e.g., `map[int][]string{1: {"video1.mp4"}, 2: {"video2.mp4", "video1.mp4"}}`).  A server can store multiple videos.
*   `network`: A list of network links, represented as tuples `(server1, server2, cost)`, where `server1` and `server2` are server IDs (integers), and `cost` is the network cost (integer, non-negative) to transfer data between those servers. The network is undirected. (e.g., `[][3]int{{1, 2, 10}, {2, 3, 5}}` means a link between servers 1 and 2 with cost 10, and a link between servers 2 and 3 with cost 5).
*   `requests`: A list of user requests, represented as tuples `(user_location, video_name)`, where `user_location` is a server ID (integer) representing the user's closest server, and `video_name` is the name of the video requested (string). (e.g., `[][2]any{{1, "video2.mp4"}, {3, "video1.mp4"}}`).

**Task:**

Implement a function that, for each request in the `requests` list, determines the optimal server to serve the video from and the total network cost to deliver the video to the user. "Optimal" means minimizing the total network cost.

Your function should return a list of results, where each result is a tuple `(serving_server, total_cost)`. `serving_server` is the ID of the server that will serve the video (integer), and `total_cost` is the total network cost to deliver the video from that server to the user (integer).

**Constraints and Edge Cases:**

1.  **Network Connectivity:** The network may not be fully connected. If a video cannot be reached from a user's location, return `(-1, -1)` for that request.
2.  **Multiple Sources:** Multiple servers may have the requested video. Your solution must find the server with the *minimum* cost path to the user.
3.  **Server Storage:** A server may not have any videos stored.
4.  **Non-existent Servers/Videos:** The input may contain requests for videos that don't exist or user locations at servers that don't exist. Return `(-1, -1)` for such requests.
5.  **Cost Minimization:**  The primary goal is to minimize the *total* cost.
6.  **Large Datasets:** The number of servers, videos, network links, and requests can be large (up to 10<sup>5</sup>). Your solution needs to be efficient (think algorithmic complexity).
7.  **Negative Costs:** Network costs are non-negative.
8.  **Self-Loops:** The network will not contain self-loops (a server connected to itself).
9.  **Parallel Edges:** The network may contain parallel edges (multiple links between the same two servers) with different costs. You should consider the minimum cost among these parallel edges.
10. **Tie Breaking:** If multiple servers can serve the video with the same minimal cost, return the server with the smallest ID.

**Example:**

```
servers = []int{1, 2, 3, 4}
videos = []string{"video1.mp4", "video2.mp4"}
storage = map[int][]string{
    1: {"video1.mp4"},
    2: {"video2.mp4", "video1.mp4"},
    3: {},
    4: {"video2.mp4"},
}
network = [][3]int{{1, 2, 10}, {2, 3, 5}, {1, 4, 20}, {4, 3, 15}}
requests = [][2]any{{1, "video2.mp4"}, {3, "video1.mp4"}}

// Expected Output:
//  [ (2, 10), (2, 15) ]

// Explanation:
// For the first request (user at server 1, video "video2.mp4"):
// - Server 2 has "video2.mp4" and the path 1 -> 2 has cost 10.
// - Server 4 has "video2.mp4" and the path 1 -> 4 has cost 20.
//  Therefore, the optimal server is 2, with a cost of 10.

// For the second request (user at server 3, video "video1.mp4"):
// - Server 1 has "video1.mp4" and the path 3 -> 2 -> 1 has cost 5 + 10 = 15.
// - Server 2 has "video1.mp4" and the path 3 -> 2 has cost 5.
// Therefore, the optimal server is 2, with a cost of 5.
```

**Evaluation Criteria:**

*   **Correctness:**  The solution must produce the correct optimal server and cost for all test cases, including edge cases.
*   **Efficiency:** The solution must be efficient enough to handle large datasets within a reasonable time limit.  Consider the time complexity of your chosen algorithm.
*   **Code Quality:** The code should be well-structured, readable, and maintainable.
*   **Error Handling:** The solution should handle invalid input gracefully and return `(-1, -1)` as specified.

This problem requires you to combine graph algorithms (shortest path), efficient data structures (potentially heaps for Dijkstra's or similar), and careful handling of various edge cases. Good luck!
