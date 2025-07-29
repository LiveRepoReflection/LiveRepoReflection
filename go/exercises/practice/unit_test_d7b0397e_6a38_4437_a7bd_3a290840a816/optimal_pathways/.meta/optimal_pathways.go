package optimal_pathways

import (
	"container/heap"
)

// FindOptimalPathways finds the minimum maximum congestion score from start to each destination
func FindOptimalPathways(n int, edges [][]int, start int, destinations []int) []int {
	// Build adjacency list representation of the graph
	graph := make(map[int][]Edge)
	maxWeight := 0
	for _, edge := range edges {
		u, v, w := edge[0], edge[1], edge[2]
		graph[u] = append(graph[u], Edge{to: v, weight: w})
		if w > maxWeight {
			maxWeight = w
		}
	}

	result := make([]int, len(destinations))
	for i, dest := range destinations {
		if dest == start {
			result[i] = 0
			continue
		}
		// Binary search over possible maximum congestion scores
		left, right := 1, maxWeight
		result[i] = -1
		for left <= right {
			mid := left + (right-left)/2
			if canReachWithMaxCongestion(graph, n, start, dest, mid) {
				result[i] = mid
				right = mid - 1
			} else {
				left = mid + 1
			}
		}
	}
	return result
}

// Edge represents a directed edge in the graph
type Edge struct {
	to     int
	weight int
}

// Item represents an item in the priority queue
type Item struct {
	node     int
	priority int
	index    int
}

// PriorityQueue implements heap.Interface
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

// canReachWithMaxCongestion checks if destination can be reached from start
// with maximum congestion score of maxCongestion
func canReachWithMaxCongestion(graph map[int][]Edge, n, start, dest, maxCongestion int) bool {
	visited := make([]bool, n)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: start, priority: 0})

	for pq.Len() > 0 {
		curr := heap.Pop(&pq).(*Item)
		if curr.node == dest {
			return true
		}
		if visited[curr.node] {
			continue
		}
		visited[curr.node] = true

		for _, edge := range graph[curr.node] {
			if !visited[edge.to] && edge.weight <= maxCongestion {
				heap.Push(&pq, &Item{
					node:     edge.to,
					priority: max(curr.priority, edge.weight),
				})
			}
		}
	}
	return false
}

// max returns the maximum of two integers
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}