## Optimal Task Assignment with Skill Constraints

**Problem Description:**

You are managing a team of `N` engineers to complete `M` tasks. Each engineer `i` has a specific set of skills, represented as a bitmask `engineerSkills[i]`. Each task `j` requires a specific set of skills, also represented as a bitmask `taskSkills[j]`. An engineer can only be assigned to a task if the engineer possesses all the skills required for that task (i.e., `(engineerSkills[i] & taskSkills[j]) == taskSkills[j]`).

Your goal is to assign *exactly one* engineer to each task such that the *total cost* of the assignment is minimized. The cost of assigning engineer `i` to task `j` is given by `cost[i][j]`. If an engineer *cannot* perform a task due to missing skills, the cost of assigning them to that task is considered infinite (represented by a very large integer, like `1e9`).

Given the `engineerSkills`, `taskSkills`, and `cost` matrices, find the minimum total cost of assigning engineers to tasks. If it is impossible to assign every task to an engineer (due to skill constraints), return `-1`.

**Input:**

*   `N` (int): The number of engineers.
*   `M` (int): The number of tasks.
*   `engineerSkills` ([]int): A slice of integers, where `engineerSkills[i]` represents the bitmask of skills possessed by engineer `i`.
*   `taskSkills` ([]int): A slice of integers, where `taskSkills[j]` represents the bitmask of skills required for task `j`.
*   `cost` ([][]int): A 2D slice of integers, where `cost[i][j]` represents the cost of assigning engineer `i` to task `j`. `cost[i][j]` is guaranteed to be non-negative.

**Constraints:**

*   `1 <= N, M <= 12` (This is crucial for complexity)
*   `0 <= engineerSkills[i] < (1 << 16)` (Each engineer can have up to 16 skills)
*   `0 <= taskSkills[j] < (1 << 16)` (Each task requires up to 16 skills)
*   `0 <= cost[i][j] <= 1000` (Cost is reasonably bounded)
*   It is guaranteed that if a task cannot be performed by an engineer, their cost is `1e9`

**Output:**

*   (int): The minimum total cost of assigning engineers to tasks. Return `-1` if it is impossible to assign every task.

**Example:**

```
N = 3
M = 3
engineerSkills = []int{7, 6, 3} // Binary: [0111, 0110, 0011]
taskSkills = []int{1, 2, 4}   // Binary: [0001, 0010, 0100]
cost = [][]int{
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
}

// Possible assignment:
// Engineer 0 (skills 7) -> Task 2 (skills 4)  Cost: 3
// Engineer 1 (skills 6) -> Task 1 (skills 2)  Cost: 5
// Engineer 2 (skills 3) -> Task 0 (skills 1)  Cost: 7
// Total cost: 3 + 5 + 7 = 15

Output: 15
```

**Challenge:**

The small constraint on `N` and `M` is intentional.  The most efficient solutions will likely involve bit manipulation, recursion, and/or dynamic programming to explore all possible valid assignments.  Carefully consider how to represent the state of your search and how to efficiently prune the search space to avoid unnecessary computations. The skill constraints add complexity to the typical assignment problem. Think about how to handle edge cases where no valid assignment exists efficiently.
