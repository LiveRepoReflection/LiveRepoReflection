package packet_routing

import (
	"container/heap"
	"math"
)

type Node struct {
	id      int
	latency int
	path    []int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].latency == pq[j].latency {
		if len(pq[i].path) == len(pq[j].path) {
			return pq[i].path[0] < pq[j].path[0]
		}
		return len(pq[i].path) < len(pq[j].path)
	}
	return pq[i].latency < pq[j].latency
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*Node))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[:n-1]
	return item
}

func FindOptimalPaths(N int, edges [][2]int, L []int, Q int, queries [][2]int) [][]int {
	// Build adjacency list
	adj := make([][]int, N)
	for _, edge := range edges {
		u, v := edge[0], edge[1]
		adj[u] = append(adj[u], v)
		adj[v] = append(adj[v], u)
	}

	results := make([][]int, Q)
	for i, query := range queries {
		S, D := query[0], query[1]
		results[i] = findPath(N, adj, L, S, D)
	}
	return results
}

func findPath(N int, adj [][]int, L []int, S, D int) []int {
	if S == D {
		return []int{S}
	}

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	visited := make([]bool, N)
	minLatency := make([]int, N)
	for i := range minLatency {
		minLatency[i] = math.MaxInt32
	}

	initialPath := []int{S}
	heap.Push(&pq, &Node{
		id:      S,
		latency: L[S] + 1,
		path:    initialPath,
	})
	minLatency[S] = L[S] + 1

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)

		if current.id == D {
			return current.path
		}

		if visited[current.id] {
			continue
		}
		visited[current.id] = true

		for _, neighbor := range adj[current.id] {
			newLatency := max(current.latency, L[neighbor]+1)
			newPath := make([]int, len(current.path)+1)
			copy(newPath, current.path)
			newPath[len(newPath)-1] = neighbor

			if newLatency < minLatency[neighbor] || 
			   (newLatency == minLatency[neighbor] && len(newPath) < len(minLatency)) {
				minLatency[neighbor] = newLatency
				heap.Push(&pq, &Node{
					id:      neighbor,
					latency: newLatency,
					path:    newPath,
				})
			}
		}
	}

	return []int{}
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}