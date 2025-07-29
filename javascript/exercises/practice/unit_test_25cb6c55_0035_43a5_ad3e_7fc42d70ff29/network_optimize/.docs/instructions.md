## Project Name

`NetworkOptimization`

## Question Description

You are tasked with designing an efficient data distribution network for a large, geographically dispersed company. The company has a central data center and multiple branch offices. Each branch office needs to receive regular data updates from the central data center. Due to bandwidth limitations and varying network conditions, you need to optimize the data distribution to minimize the overall cost.

The network can be represented as a weighted, undirected graph. The nodes represent the data center and branch offices, and the edges represent network connections between them. The weight of each edge represents the cost (e.g., bandwidth usage, latency penalty) of transmitting one unit of data across that connection.

**Data Requirements:**

Each branch office has a specific data demand, representing the amount of data it needs to receive per unit of time. The central data center can supply data to any number of branch offices simultaneously.

**Delivery Method:**

Data can be sent from the central data center to each branch office via one or more "data paths". A data path is a sequence of connected edges in the network graph. Each path has a cost associated with it, which is the sum of the weights of the edges in the path.

**Optimization Goal:**

Your task is to determine the optimal set of data paths to use for each branch office, such that:

1.  **All data demands are met:** Each branch office receives the amount of data it requires.
2.  **The total cost is minimized:** The sum of the costs of all data paths used is as small as possible.
3.  **Load Balancing:** To avoid congestion and ensure robustness, the data flow through each edge should be balanced. No single edge should carry significantly more data than other edges. Define a "congestion factor" for each edge as the ratio of the data flowing through the edge to the edge's capacity. The maximum congestion factor across all edges in the network should be minimized. You can assume all edges have the same capacity of '1', so you need to minimize the maximum flow going through each edge.

**Input:**

Your function will receive the following inputs:

*   `network`: An adjacency list representing the network graph. Each key is a node (string representing the data center or branch office name), and the value is an array of objects, where each object represents an edge to a neighboring node and its cost: `[{to: 'neighbor_node_name', cost: 5}]`. The data center will have the name `"data_center"`.
*   `demands`: An object where the keys are branch office names (strings), and the values are the data demands (numbers) for each branch office. For example: `{ "branch_A": 10, "branch_B": 5 }`.
*   `maxPaths`: An integer representing the maximum number of data paths allowed per branch office. Limiting the number of paths can encourage better load balancing.

**Output:**

Your function should return an object where the keys are branch office names (strings), and the values are an array of data paths. Each data path should be an array of node names (strings) representing the path from the data center to the branch office. The paths should be sorted in ascending order of their costs.
For example:

```javascript
{
  "branch_A": [
    ["data_center", "node_1", "branch_A"],
    ["data_center", "node_2", "node_3", "branch_A"]
  ],
  "branch_B": [
    ["data_center", "node_4", "branch_B"]
  ]
}
```

**Constraints:**

*   The number of nodes in the network can be up to 100.
*   The data demand for each branch office is a positive integer.
*   The cost of each edge is a positive integer.
*   The maximum number of paths per branch office is between 1 and 5, inclusive.
*   You can assume that there is at least one path from the data center to each branch office.
*   The execution time of your function should be optimized. Solutions that take excessively long to run will be considered incorrect.
*   The solution must meet the requirements of data demand and minimize total cost and load balancing (congestion factor).

**Example:**

```javascript
const network = {
  "data_center": [{ to: "branch_A", cost: 1 }, { to: "branch_B", cost: 3 }],
  "branch_A": [{ to: "data_center", cost: 1 }],
  "branch_B": [{ to: "data_center", cost: 3 }]
};

const demands = {
  "branch_A": 5,
  "branch_B": 2
};

const maxPaths = 2;

// Expected Output (May Vary based on Load Balancing)
// {
//   "branch_A": [
//     ["data_center", "branch_A"] // Cost: 1, Used 5 times
//   ],
//   "branch_B": [
//     ["data_center", "branch_B"] // Cost: 3, Used 2 times
//   ]
// }
```

**Challenge:**

This problem requires you to combine graph traversal algorithms (e.g., Dijkstra's, A\*), optimization techniques (e.g., greedy algorithms, linear programming - though a full linear programming implementation might be too complex within the time constraints), and load balancing considerations to arrive at a solution that satisfies all constraints within a reasonable time. The optimal solution will likely involve trade-offs between path cost and load balancing.

Good luck!
