package network_scheduler

import (
	"sort"
)

// ScheduleTasks assigns each task to a node such that the tasks scheduled sequentially on each node
// can finish before their deadline. Each node processes tasks one after another (non-overlapping).
// If no valid assignment is possible, the function returns an empty slice.
func ScheduleTasks(N, M int, C, P, D []int) []int {
	// assignments holds the node assignment (1-indexed) for each task (in the original order)
	assignments := make([]int, M)
	// finishTime holds the current accumulated processing time on each node
	finishTime := make([]int, N)

	// Define a structure to hold task information along with its original index.
	type taskInfo struct {
		idx int
		p   int
		d   int
	}
	tasks := make([]taskInfo, M)
	for i := 0; i < M; i++ {
		tasks[i] = taskInfo{
			idx: i,
			p:   P[i],
			d:   D[i],
		}
	}
	// Pre-check: each task must be eligible to run on at least one node.
	for _, t := range tasks {
		eligible := false
		for j := 0; j < N; j++ {
			if C[j] >= t.p {
				eligible = true
				break
			}
		}
		if !eligible {
			return []int{}
		}
	}

	// Sort tasks by their deadline in ascending order.
	sort.Slice(tasks, func(i, j int) bool {
		return tasks[i].d < tasks[j].d
	})

	// Greedily assign each task to an eligible node.
	for _, t := range tasks {
		selectedNode := -1
		minFinish := int(^uint(0) >> 1) // set to maximum int value
		// Try to assign the task to the node that can finish it earliest while meeting the deadline.
		for node := 0; node < N; node++ {
			if C[node] >= t.p {
				candidateFinish := finishTime[node] + t.p
				if candidateFinish <= t.d && candidateFinish < minFinish {
					minFinish = candidateFinish
					selectedNode = node
				}
			}
		}
		if selectedNode == -1 {
			// No node can schedule this task without missing its deadline.
			return []int{}
		}
		// Update the finish time for the selected node.
		finishTime[selectedNode] += t.p
		// Save the assignment (convert 0-indexed node to 1-indexed).
		assignments[t.idx] = selectedNode + 1
	}

	return assignments
}