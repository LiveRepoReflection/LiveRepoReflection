package service_routing

import (
	"container/heap"
)

type State struct {
	cost int
	node int
	path []int
}

// PriorityQueue implements heap.Interface for States.
type PriorityQueue []*State

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq PriorityQueue) Swap(i, j int) { 
	pq[i], pq[j] = pq[j], pq[i] 
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*State))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// contains checks if slice contains a given value.
func contains(slice []int, value int) bool {
	for _, v := range slice {
		if v == value {
			return true
		}
	}
	return false
}

// RouteRequest finds the optimal routing path from entry to target.
// It returns a slice of integers representing the sequence of microservice IDs in the path.
// If no valid path exists that respects capacity constraints, it returns an empty slice.
func RouteRequest(N int, connections [][]bool, capacities []int, entry int, target int, latencyMatrix [][]int) []int {
	// If entry has no capacity, no path is possible.
	if capacities[entry] <= 0 {
		return []int{}
	}
	// If entry equals target, consume capacity and return the single node.
	if entry == target {
		capacities[entry]--
		return []int{entry}
	}

	// Priority queue for Dijkstra-like search.
	pq := &PriorityQueue{}
	heap.Init(pq)

	start := &State{
		cost: 0,
		node: entry,
		path: []int{entry},
	}
	heap.Push(pq, start)

	// Use a map to record the best cost found for a given state (node + visited combination).
	// The key is a string composed of node and visited nodes in the path.
	visitedMap := make(map[string]int)

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*State)
		// If current reaches target, simulate consumption of capacity and return path.
		if current.node == target {
			// Decrement capacity for each node in the path.
			for _, node := range current.path {
				capacities[node]--
			}
			return current.path
		}

		// Explore neighbors.
		for v := 0; v < N; v++ {
			// Proceed only if there is a connection from current.node to v.
			if !connections[current.node][v] {
				continue
			}
			// v must have capacity available.
			if capacities[v] <= 0 {
				continue
			}
			// Avoid cycles: do not revisit nodes already in the current path.
			if contains(current.path, v) {
				continue
			}
			newCost := current.cost + latencyMatrix[current.node][v]
			newPath := make([]int, len(current.path))
			copy(newPath, current.path)
			newPath = append(newPath, v)

			// Create a key for the state: using the current node v and the visited set.
			key := stateKey(v, newPath)
			if prevCost, ok := visitedMap[key]; ok {
				if newCost >= prevCost {
					continue
				}
			}
			visitedMap[key] = newCost

			newState := &State{
				cost: newCost,
				node: v,
				path: newPath,
			}
			heap.Push(pq, newState)
		}
	}
	// If no valid path is found, return empty slice.
	return []int{}
}

// stateKey generates a key string based on current node and visited nodes in the path.
func stateKey(node int, path []int) string {
	// Simple key: node:visited nodes in order separated by commas.
	key := ""
	for _, v := range path {
		key += string(rune(v)) + ","
	}
	key += string(rune(node))
	return key
}