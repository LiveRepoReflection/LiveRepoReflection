package time_weighted_path

import (
	"container/heap"
	"math"
)

type Edge struct {
	to     int
	weight int
}

type State struct {
	node     int
	time     int
	edgesUsed int
}

type PriorityQueue []*State

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].time < pq[j].time
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*State)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func FindMinTime(n int, edges [][]int, start int, end int, k int, maxTime int) int {
	graph := make([][]Edge, n)
	for _, edge := range edges {
		u, v, w := edge[0], edge[1], edge[2]
		graph[u] = append(graph[u], Edge{v, w})
	}

	minTime := make([][]int, n)
	for i := range minTime {
		minTime[i] = make([]int, k+1)
		for j := range minTime[i] {
			minTime[i][j] = math.MaxInt32
		}
	}
	minTime[start][0] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &State{node: start, time: 0, edgesUsed: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*State)

		if current.node == end {
			return current.time
		}

		if current.edgesUsed == k {
			continue
		}

		for _, edge := range graph[current.node] {
			newTime := current.time + edge.weight
			newEdgesUsed := current.edgesUsed + 1

			if newTime > maxTime {
				continue
			}

			if newTime < minTime[edge.to][newEdgesUsed] {
				minTime[edge.to][newEdgesUsed] = newTime
				heap.Push(&pq, &State{
					node:      edge.to,
					time:      newTime,
					edgesUsed: newEdgesUsed,
				})
			}
		}
	}

	return -1
}