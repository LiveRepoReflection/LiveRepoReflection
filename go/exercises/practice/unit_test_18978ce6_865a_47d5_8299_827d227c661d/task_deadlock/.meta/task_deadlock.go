package task_deadlock

import (
	"sort"
)

func DetectDeadlock(tasks []Task, capacity int) []int {
	// Build dependency graph and reverse graph
	graph := make(map[int][]int)
	inDegree := make(map[int]int)
	nodes := make(map[int]bool)

	for _, task := range tasks {
		nodes[task.ID] = true
		inDegree[task.ID] = 0
	}

	for _, task := range tasks {
		for _, dep := range task.Dependencies {
			graph[dep] = append(graph[dep], task.ID)
			inDegree[task.ID]++
		}
	}

	// Find all nodes with no dependencies
	queue := make([]int, 0)
	for node, deg := range inDegree {
		if deg == 0 {
			queue = append(queue, node)
		}
	}

	// Kahn's algorithm for topological sort
	processed := 0
	for len(queue) > 0 && capacity > 0 {
		currentBatchSize := min(len(queue), capacity)
		capacity -= currentBatchSize

		for i := 0; i < currentBatchSize; i++ {
			node := queue[0]
			queue = queue[1:]
			processed++

			for _, neighbor := range graph[node] {
				inDegree[neighbor]--
				if inDegree[neighbor] == 0 {
					queue = append(queue, neighbor)
				}
			}
		}
	}

	// If we processed all nodes, no deadlock
	if processed == len(nodes) {
		return []int{}
	}

	// Otherwise find the smallest cycle
	return findSmallestCycle(graph, nodes, inDegree)
}

func findSmallestCycle(graph map[int][]int, nodes map[int]bool, inDegree map[int]int) []int {
	visited := make(map[int]bool)
	onStack := make(map[int]bool)
	cycle := make([]int, 0)
	minCycle := make([]int, 0)

	var dfs func(int, int) bool
	dfs = func(node, parent int) bool {
		visited[node] = true
		onStack[node] = true
		cycle = append(cycle, node)

		for _, neighbor := range graph[node] {
			if !visited[neighbor] {
				if dfs(neighbor, node) {
					return true
				}
			} else if onStack[neighbor] {
				// Found a cycle
				startIdx := 0
				for i := len(cycle) - 1; i >= 0; i-- {
					if cycle[i] == neighbor {
						startIdx = i
						break
					}
				}

				currentCycle := cycle[startIdx:]
				if len(minCycle) == 0 || len(currentCycle) < len(minCycle) {
					minCycle = make([]int, len(currentCycle))
					copy(minCycle, currentCycle)
				} else if len(currentCycle) == len(minCycle) {
					// If same length, pick lexicographically smaller
					sort.Ints(currentCycle)
					sort.Ints(minCycle)
					if currentCycle[0] < minCycle[0] {
						minCycle = make([]int, len(currentCycle))
						copy(minCycle, currentCycle)
					}
				}
				return true
			}
		}

		onStack[node] = false
		cycle = cycle[:len(cycle)-1]
		return false
	}

	// Find all nodes that are part of cycles (inDegree > 0)
	for node := range nodes {
		if inDegree[node] > 0 && !visited[node] {
			dfs(node, -1)
		}
	}

	if len(minCycle) > 0 {
		sort.Ints(minCycle)
		return minCycle
	}

	// Shouldn't reach here if there's a deadlock
	return []int{}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}