## Project Name

```
optimal-route-planner
```

## Question Description

You are tasked with building an optimal route planner for a delivery service operating in a complex urban environment. The city is represented as a weighted graph, where nodes represent delivery locations and edges represent roads connecting them. Each road has a specific travel time (weight).

However, the traffic conditions in the city are dynamic and unpredictable. To account for this, each road also has a *congestion factor* associated with it that changes every minute. The congestion factor is a real number between 0.5 and 2.0 (inclusive). A congestion factor of 1.0 indicates normal traffic; less than 1.0 indicates lighter traffic (faster travel), and greater than 1.0 indicates heavier traffic (slower travel).

Your goal is to implement a function that finds the *minimum travel time route* between a given start and end location, considering the dynamic congestion factors.

**Specific Requirements:**

1.  **Graph Representation:** The city map is provided as an adjacency list where keys are node IDs (strings) and values are arrays of objects, each representing a road to another node. Each road object has the following structure:

    ```javascript
    {
        to: "nodeId", // string: ID of the destination node
        travelTime: 10, // number: base travel time in minutes
        congestionFunction: (currentTime) => { return congestionFactor; } // function that returns the congestion factor at a given currentTime (in minutes, relative to the start of the route)
    }
    ```

2.  **Dynamic Congestion:** The `congestionFunction` for each road takes the current time (in minutes, relative to the start of the route) as input and returns the congestion factor *at that specific time*. This function needs to be called every time the cost of using a specific road at a specific time needs to be evaluated.

3.  **Time-Dependent Cost:** The actual travel time on a road is calculated by multiplying the base `travelTime` with the `congestionFactor` at the *time when the delivery vehicle enters that road*.

4.  **Optimization:** The function must find the *minimum travel time route*. Consider efficiency when choosing your algorithm, especially for larger city maps.

5.  **Constraints:**

    *   The graph can be large (hundreds or thousands of nodes).
    *   The congestion functions can be complex and computationally expensive.
    *   The function needs to be reasonably fast (sub-second execution time for moderately sized graphs).
    *   Assume that the congestion factors are deterministic and do not change while traversing a single road. This means, you only need to sample the congestion function at the entry time of the road.
    *   Node IDs are unique strings.
    *   `currentTime` passed to the `congestionFunction` will always be a non-negative number.

6.  **Output:**

    The function should return an object with the following structure:

    ```javascript
    {
        totalTime: 123.45, // number: Total travel time in minutes along the optimal route (rounded to two decimal places).
        route: ["nodeA", "nodeB", "nodeC"] // array of strings: Ordered list of node IDs representing the optimal route, including the start and end nodes.
    }
    ```

    If no route is found, return:

    ```javascript
    {
        totalTime: -1,
        route: []
    }
    ```

**Example:**

```javascript
const cityMap = {
    "A": [{to: "B", travelTime: 10, congestionFunction: (t) => 1.0}],
    "B": [{to: "C", travelTime: 15, congestionFunction: (t) => t > 10 ? 1.5 : 0.8}],
    "C": []
};

const start = "A";
const end = "C";

const result = findOptimalRoute(cityMap, start, end);

// Possible valid result:
// { totalTime: 22.00, route: [ 'A', 'B', 'C' ] }
// (10 * 1.0) + (15 * 0.8) = 10 + 12 = 22

```

**Hint:** Consider using a modified version of Dijkstra's algorithm. You'll need to track the time taken to reach each node and use this time to query the congestion functions. Think about how to efficiently explore the graph while minimizing the total travel time.

This problem requires a combination of graph traversal, dynamic cost calculation, and optimization techniques. Good luck!
