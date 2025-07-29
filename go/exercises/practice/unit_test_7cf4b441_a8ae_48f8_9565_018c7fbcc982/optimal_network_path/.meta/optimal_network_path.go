package optimal_network_path

import (
	"container/heap"
)

type Edge struct {
	to       int
	cost     int
	latency  int
}

type Node struct {
	id       int
	cost     int
	latency  int
	hops     int
	index    int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].hops == pq[j].hops {
		if pq[i].cost == pq[j].cost {
			return pq[i].latency < pq[j].latency
		}
		return pq[i].cost < pq[j].cost
	}
	return pq[i].hops < pq[j].hops
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Node)
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

func OptimalNetworkPath(N int, edges [][]int, source int, destination int, maxCost int, maxLatency int) int {
	if source == destination {
		return 0
	}

	graph := make(map[int][]Edge)
	for _, edge := range edges {
		from, to, cost, latency := edge[0], edge[1], edge[2], edge[3]
		graph[from] = append(graph[from], Edge{to, cost, latency})
		graph[to] = append(graph[to], Edge{from, cost, latency})
	}

	visited := make(map[int]map[int]map[int]bool)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	heap.Push(&pq, &Node{
		id:      source,
		cost:    0,
		latency: 0,
		hops:    0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Node)

		if current.id == destination {
			return current.hops
		}

		if _, exists := visited[current.id]; !exists {
			visited[current.id] = make(map[int]map[int]bool)
		}
		if _, exists := visited[current.id][current.cost]; !exists {
			visited[current.id][current.cost] = make(map[int]bool)
		}
		if visited[current.id][current.cost][current.latency] {
			continue
		}
		visited[current.id][current.cost][current.latency] = true

		for _, edge := range graph[current.id] {
			newCost := current.cost + edge.cost
			newLatency := current.latency + edge.latency
			newHops := current.hops + 1

			if newCost > maxCost || newLatency > maxLatency {
				continue
			}

			if _, exists := visited[edge.to]; !exists {
				visited[edge.to] = make(map[int]map[int]bool)
			}
			if _, exists := visited[edge.to][newCost]; !exists {
				visited[edge.to][newCost] = make(map[int]bool)
			}
			if visited[edge.to][newCost][newLatency] {
				continue
			}

			heap.Push(&pq, &Node{
				id:      edge.to,
				cost:    newCost,
				latency: newLatency,
				hops:    newHops,
			})
		}
	}

	return -1
}