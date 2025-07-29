Okay, I'm ready to craft a challenging coding problem. Here's the description:

**Problem Title:** Distributed Transaction Orchestration

**Problem Description:**

You are building a distributed transaction orchestration service. This service is responsible for managing transactions that span multiple independent microservices. A transaction consists of a sequence of operations, each performed by a different microservice. Each operation can either succeed or fail. If any operation in the transaction fails, the entire transaction must be rolled back by invoking a corresponding compensation operation on each microservice that successfully completed its part of the transaction.

Your task is to implement a function that takes a directed acyclic graph (DAG) representing a transaction and determines the optimal execution order of operations to minimize the expected rollback cost in case of failure.

**Input:**

*   A DAG represented as an adjacency list, where each node represents an operation performed by a microservice. The nodes are labeled with unique integer IDs from 0 to N-1, where N is the total number of operations.
*   Each node in the DAG has the following properties:
    *   `service_id`: The ID of the microservice responsible for performing the operation.
    *   `success_probability`: The probability (between 0.0 and 1.0 inclusive) that the operation will succeed.
    *   `operation_cost`: The cost (a non-negative integer) incurred if the operation succeeds.
    *   `rollback_cost`: The cost (a non-negative integer) incurred if the operation needs to be rolled back due to a failure elsewhere in the transaction.

**Output:**

*   An ordered list of node IDs representing the optimal execution order of operations in the transaction. The execution order must satisfy the topological order of the DAG.
*   If there are multiple optimal execution orders with the same minimum expected rollback cost, return any one of them.

**Constraints:**

*   The input DAG is guaranteed to be a valid directed acyclic graph.
*   The number of nodes (N) in the DAG can be up to 1000.
*   The number of edges in the DAG can be up to 5000.
*   All costs are non-negative integers and fit within a 32-bit integer.
*   The success probability for each operation is between 0.0 and 1.0 inclusive.
*   The graph may contain nodes with no dependencies (source nodes) and nodes with no dependents (sink nodes).

**Optimization Requirement:**

*   The solution should minimize the expected rollback cost. This is calculated as the sum of the rollback costs of all operations multiplied by the probability that they will need to be rolled back.

**Edge Cases:**

*   Empty DAG (no operations).
*   DAG with only one operation.
*   DAG with multiple source nodes.
*   DAG with multiple sink nodes.
*   DAG with operations that have a success probability of 0.0 or 1.0.
*   Cycles in the graph are not allowed

**Example (Illustrative):**

Let's say you have a DAG with three nodes:

*   Node 0: `service_id=1, success_probability=0.9, operation_cost=10, rollback_cost=5`
*   Node 1: `service_id=2, success_probability=0.8, operation_cost=15, rollback_cost=8`
*   Node 2: `service_id=3, success_probability=0.7, operation_cost=20, rollback_cost=10`

And the edges are: 0 -> 1, 1 -> 2.

Two possible execution orders are [0, 1, 2] and any other topological sorted order which in this case is only [0, 1, 2]. The optimal ordering is the one that minimizes the expected rollback cost.

**Judging Criteria:**

The solution will be judged based on its correctness (producing a valid topological sort and a minimized expected rollback cost) and its efficiency (ability to handle large DAGs within a reasonable time limit). You need to consider optimal data structures and algorithms to achieve good performance. A brute-force approach that explores all possible topological orderings is unlikely to pass all test cases.
