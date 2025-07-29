Okay, here's a challenging coding problem designed to test advanced Python skills.

### Project Name

```
distributed-data-aggregation
```

### Question Description

You are designing a distributed system for aggregating numerical data from a large number of edge devices. These devices are organized into a hierarchical tree structure. Each device collects a stream of numerical measurements. The goal is to efficiently compute various aggregate statistics (min, max, sum, average) for the data originating from all devices within a given subtree.

The system consists of the following components:

1.  **Edge Devices:** Leaf nodes in the tree. Each device continuously generates numerical measurements.

2.  **Intermediate Nodes:** Internal nodes in the tree. These nodes receive data from their children, aggregate it, and forward the aggregated results to their parent.

3.  **Root Node:** The root of the tree. It receives the final aggregated results for the entire system.

4.  **Query System:** This system allows users to query for aggregate statistics for any subtree in the hierarchy. The query specifies the root of the subtree of interest (which could be any node in the tree) and the desired statistic (min, max, sum, or average).

**Your task is to implement the aggregation logic for the intermediate nodes and the query system.**

**Specific Requirements:**

*   **Tree Representation:** The tree structure is represented using a nested dictionary. Each key in the dictionary is a node ID (string). The value associated with each key is another dictionary with the following keys:
    *   `'children'`: A list of node IDs representing the children of this node. This list can be empty for leaf nodes.
    *   `'data'`: A list of numerical data points received from its children (for intermediate nodes) or generated locally (for leaf nodes). This list will be empty initially for intermediate nodes.
*   **Aggregation Logic:** Intermediate nodes must continuously update their aggregated statistics as they receive data from their children. Your solution should efficiently maintain these aggregates.
*   **Query Processing:** The query system should efficiently compute the requested aggregate statistic for the specified subtree. You need to implement a function that takes the tree, the root node ID of the subtree, and the desired statistic as input and returns the result.
*   **Efficiency:** The system should be designed to handle a large number of devices and a high volume of data. Consider algorithmic efficiency when implementing the aggregation and query processing logic.
*   **Error Handling:** The system should handle cases where a node ID is not found in the tree or an invalid statistic is requested.
*   **Data Types:** All numerical data points are floating-point numbers.

**Constraints:**

*   The tree can have an arbitrary depth and branching factor.
*   The number of edge devices can be very large (up to 10<sup>6</sup>).
*   The data stream from each edge device is continuous.
*   Queries should be answered as quickly as possible.
*   Memory usage should be optimized to avoid storing excessive amounts of data at intermediate nodes. Consider using a sliding window or other techniques to limit the amount of data stored.
*   The aggregate statistics should be accurate, even in the face of floating-point precision issues.

**Bonus Challenges:**

*   Implement a mechanism for handling device failures. If a device fails, its data should be excluded from the aggregate statistics.
*   Implement support for weighted averages, where each device has a weight associated with its data.
*   Optimize the system for parallel processing using multi-threading or multiprocessing.
*   Consider how to best choose data structures for performance, and defend your choices.
