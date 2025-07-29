package network_hops

import (
	"container/heap"
)

type Edge struct {
	to     int
	latency int
}

type State struct {
	node    int
	latency int
	hops    int
}

type PriorityQueue []*State

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].hops == pq[j].hops {
		return pq[i].latency < pq[j].latency
	}
	return pq[i].hops < pq[j].hops
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

func FindMinHops(N int, edges [][]int, S int, D int, L int) int {
	if S == D {
		if L >= 0 {
			return 0
		}
		return -1
	}

	graph := make(map[int][]Edge)
	for _, edge := range edges {
		u, v, latency := edge[0], edge[1], edge[2]
		graph[u] = append(graph[u], Edge{v, latency})
	}

	minLatency := make([]int, N)
	minHops := make([]int, N)
	for i := range minLatency {
		minLatency[i] = L + 1
		minHops[i] = N + 1
	}
	minLatency[S] = 0
	minHops[S] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &State{S, 0, 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*State)

		if current.node == D {
			return current.hops
		}

		if current.latency > minLatency[current.node] || current.hops > minHops[current.node] {
			continue
		}

		for _, edge := range graph[current.node] {
			newLatency := current.latency + edge.latency
			newHops := current.hops + 1

			if newLatency > L {
				continue
			}

			if newLatency < minLatency[edge.to] || newHops < minHops[edge.to] {
				minLatency[edge.to] = newLatency
				minHops[edge.to] = newHops
				heap.Push(&pq, &State{edge.to, newLatency, newHops})
			}
		}
	}

	return -1
}