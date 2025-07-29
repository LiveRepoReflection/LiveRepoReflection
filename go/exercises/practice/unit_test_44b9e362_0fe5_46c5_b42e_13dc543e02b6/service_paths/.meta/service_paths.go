package service_paths

import (
	"container/heap"
)

type Path struct {
	cost int
	node int
}

type MinHeap []Path

func (h MinHeap) Len() int           { return len(h) }
func (h MinHeap) Less(i, j int) bool { return h[i].cost < h[j].cost }
func (h MinHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *MinHeap) Push(x interface{}) {
	*h = append(*h, x.(Path))
}

func (h *MinHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func FindKCheapestPaths(numServices int, edges [][3]int, requests [][2]int, k int) [][]int {
	// Build adjacency list
	adj := make([][]Path, numServices)
	for _, edge := range edges {
		u, v, w := edge[0], edge[1], edge[2]
		adj[u] = append(adj[u], Path{cost: w, node: v})
	}

	results := make([][]int, len(requests))

	for i, req := range requests {
		start, end := req[0], req[1]
		if start == end {
			if start < numServices {
				results[i] = []int{0}
			} else {
				results[i] = []int{}
			}
			continue
		}

		// Priority queue for Dijkstra's algorithm
		pq := &MinHeap{}
		heap.Init(pq)
		heap.Push(pq, Path{cost: 0, node: start})

		// To store k shortest paths
		shortestPaths := make([]int, 0, k)

		for pq.Len() > 0 && len(shortestPaths) < k {
			current := heap.Pop(pq).(Path)
			currentCost, currentNode := current.cost, current.node

			if currentNode == end {
				shortestPaths = append(shortestPaths, currentCost)
				continue
			}

			for _, neighbor := range adj[currentNode] {
				newCost := currentCost + neighbor.cost
				heap.Push(pq, Path{cost: newCost, node: neighbor.node})
			}
		}

		results[i] = shortestPaths
	}

	return results
}