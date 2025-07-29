package task_orchestration

import (
	"errors"
	"sort"
)

// OptimalAssignment assigns m tasks to n worker nodes while minimizing the makespan
// and respecting the resource capacity constraints. If failedNode is not -1, that node is considered unavailable.
func OptimalAssignment(n int, m int, capacities []int, requirements []int, times [][]int, failedNode int) (map[int][]int, error) {
	assignment := make(map[int][]int)
	// Initialize assignments for each node. For the failed node, the assignment should remain empty.
	for i := 0; i < n; i++ {
		assignment[i] = []int{}
	}

	// Copy of capacities to track remaining capacity.
	nodeCapacityLeft := make([]int, n)
	for i := 0; i < n; i++ {
		nodeCapacityLeft[i] = capacities[i]
	}

	// Track the cumulative processing time (makespan contribution) for each node.
	nodeTime := make([]int, n)

	// Create a list of task indices and sort them in descending order by resource requirement.
	// For tasks with equal resource requirements, sort by the maximum processing time among available nodes.
	taskOrder := make([]int, m)
	for i := 0; i < m; i++ {
		taskOrder[i] = i
	}
	sort.Slice(taskOrder, func(i, j int) bool {
		ti := taskOrder[i]
		tj := taskOrder[j]
		if requirements[ti] != requirements[tj] {
			return requirements[ti] > requirements[tj]
		}
		// Tie-breaker: task with higher minimum processing time on available nodes comes first.
		minTimeI := int(1e9)
		minTimeJ := int(1e9)
		for k := 0; k < n; k++ {
			if k == failedNode {
				continue
			}
			if times[ti][k] < minTimeI {
				minTimeI = times[ti][k]
			}
			if times[tj][k] < minTimeJ {
				minTimeJ = times[tj][k]
			}
		}
		return minTimeI > minTimeJ
	})

	// Greedy assignment: For each task, choose the node (excluding the failed node) that
	// can accommodate the task's resource requirement and results in the minimum finishing time.
	for _, task := range taskOrder {
		candidate := -1
		candidateFinishTime := int(1e9)
		for j := 0; j < n; j++ {
			if j == failedNode {
				continue
			}
			if nodeCapacityLeft[j] < requirements[task] {
				continue
			}
			finishTime := nodeTime[j] + times[task][j]
			if finishTime < candidateFinishTime {
				candidateFinishTime = finishTime
				candidate = j
			}
		}
		if candidate == -1 {
			return map[int][]int{}, errors.New("no feasible assignment found")
		}
		assignment[candidate] = append(assignment[candidate], task)
		nodeTime[candidate] += times[task][candidate]
		nodeCapacityLeft[candidate] -= requirements[task]
	}

	return assignment, nil
}