## Question: Optimal Evacuation Route Planning

**Problem Description:**

A large technology company, "MegaCorp," has its headquarters in a skyscraper with *N* floors. Each floor has *M* offices connected by corridors. The building is represented as a grid graph where each node `(i, j)` represents an office on floor *i* and at position *j*.  `i` ranges from `1` to `N` (inclusive) and `j` ranges from `1` to `M` (inclusive).

Due to an unforeseen emergency, MegaCorp needs to evacuate all employees from the building as quickly as possible.  There are *K* evacuation points located on the ground floor (floor 1). Each evacuation point has a limited capacity `C_k`, representing the maximum number of employees it can handle.

Each office `(i, j)` contains a certain number of employees, `E(i, j)`. Employees can move from one office to an adjacent office (up, down, left, right) in one time unit. Employees can also move from floor *i* to floor *i-1* (down one floor) in one time unit.  Moving from floor *i* to floor *i+1* is **not** allowed (the elevators are disabled).

The goal is to determine the optimal evacuation plan that minimizes the *maximum evacuation time* for any employee.  The evacuation time for an employee is the time it takes for them to reach an evacuation point on the ground floor. The evacuation plan must specify which evacuation point each office's employees should evacuate to.

**Constraints:**

*   `1 <= N <= 50` (Number of floors)
*   `1 <= M <= 50` (Number of offices per floor)
*   `1 <= K <= 5`  (Number of evacuation points)
*   `1 <= E(i, j) <= 100` (Number of employees in each office)
*   `1 <= C_k <= 5000` (Capacity of each evacuation point)
*   Total number of employees in the building will **not** exceed the total capacity of all evacuation points.
*   You can assume all values are integers.

**Input:**

The input will be provided as follows:

*   `N`, `M`, `K`: Integers representing the number of floors, number of offices per floor, and number of evacuation points, respectively.
*   `E`: A 2D array of size `N x M` representing the number of employees in each office. `E[i][j]` represents the number of employees at floor `i+1`, office `j+1`.
*   `EvacuationPoints`: An array of size `K`. Each element `EvacuationPoints[k]` represents the column index (from 1 to M) of the *k*-th evacuation point on the ground floor (floor 1).
*   `C`: An array of size `K`, where `C[k]` is the capacity of the *k*-th evacuation point.

**Output:**

The minimum possible value of the *maximum evacuation time* for any employee, given an optimal evacuation plan.

**Example:**

```
N = 3, M = 3, K = 2
E = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
EvacuationPoints = [1, 3] // Evacuation points at office 1 and 3 on floor 1
C = [20, 25] // Capacity of evacuation point 1 is 20, and of evacuation point 2 is 25.
```

**Judging Criteria:**

The solution will be judged based on its correctness and efficiency. Solutions that are significantly slower than the optimal solution may not pass all test cases.  Partial credit may be awarded for solutions that pass some test cases, but a fully correct and efficient solution is required for full marks. Consider edge cases and optimize your solution for speed. Solutions that do not scale well with increasing N, M, and K will not be considered efficient.
