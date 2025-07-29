package network_optimize

import (
	"container/heap"
	"math"
)

type Edge struct {
	to       int
	capacity int
	latency  int
}

type Path struct {
	nodes     []int
	minCap    int
	totalLat  int
}

type PriorityQueueItem struct {
	node      int
	minCap    int
	totalLat  int
	path      []int
	index     int
}

type PriorityQueue []*PriorityQueueItem

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	throughputI := float64(pq[i].minCap) / float64(pq[i].totalLat)
	throughputJ := float64(pq[j].minCap) / float64(pq[j].totalLat)
	return throughputI > throughputJ
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*PriorityQueueItem)
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

func OptimizeNetwork(n int, edges [][3]int, source int, destination int, latency map[[2]int]int, dataSize int) ([]int, float64) {
	graph := make([][]Edge, n)
	for _, e := range edges {
		u, v, cap := e[0], e[1], e[2]
		graph[u] = append(graph[u], Edge{
			to:       v,
			capacity: cap,
			latency:  latency[[2]int{u, v}],
		})
	}

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	heap.Push(&pq, &PriorityQueueItem{
		node:     source,
		minCap:   math.MaxInt32,
		totalLat: 0,
		path:     []int{source},
	})

	bestPath := []int{}
	bestThroughput := 0.0

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*PriorityQueueItem)

		if current.node == destination {
			currentThroughput := float64(current.minCap) / float64(current.totalLat)
			if currentThroughput > bestThroughput {
				bestThroughput = currentThroughput
				bestPath = current.path
			}
			continue
		}

		for _, edge := range graph[current.node] {
			newMinCap := min(current.minCap, edge.capacity)
			newTotalLat := current.totalLat + edge.latency
			newPath := make([]int, len(current.path)+1)
			copy(newPath, current.path)
			newPath[len(newPath)-1] = edge.to

			heap.Push(&pq, &PriorityQueueItem{
				node:     edge.to,
				minCap:   newMinCap,
				totalLat: newTotalLat,
				path:     newPath,
			})
		}
	}

	if len(bestPath) == 0 {
		return nil, 0.0
	}
	return bestPath, bestThroughput
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}