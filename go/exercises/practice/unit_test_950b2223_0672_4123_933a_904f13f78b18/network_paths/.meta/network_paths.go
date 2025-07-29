package networkpaths

import (
	"container/heap"
)

type NetworkPathOptimizer struct {
	graph       map[int]map[int]int
	disabled    map[int]bool
}

func NewNetworkPathOptimizer(edges [][]int) *NetworkPathOptimizer {
	npo := &NetworkPathOptimizer{
		graph:    make(map[int]map[int]int),
		disabled: make(map[int]bool),
	}

	for _, edge := range edges {
		npo.AddEdge(edge[0], edge[1], edge[2])
	}

	return npo
}

func (npo *NetworkPathOptimizer) AddEdge(router1, router2, latency int) {
	if npo.disabled[router1] || npo.disabled[router2] {
		return
	}

	if npo.graph[router1] == nil {
		npo.graph[router1] = make(map[int]int)
	}
	if npo.graph[router2] == nil {
		npo.graph[router2] = make(map[int]int)
	}

	if existingLatency, exists := npo.graph[router1][router2]; !exists || latency < existingLatency {
		npo.graph[router1][router2] = latency
		npo.graph[router2][router1] = latency
	}
}

func (npo *NetworkPathOptimizer) RemoveEdge(router1, router2 int) {
	delete(npo.graph[router1], router2)
	delete(npo.graph[router2], router1)
}

func (npo *NetworkPathOptimizer) DisableRouter(router int) {
	npo.disabled[router] = true
	for neighbor := range npo.graph[router] {
		delete(npo.graph[neighbor], router)
	}
	delete(npo.graph, router)
}

func (npo *NetworkPathOptimizer) EnableRouter(router int) {
	delete(npo.disabled, router)
}

func (npo *NetworkPathOptimizer) FindLowestLatencyPath(start, end int) (int, []int) {
	if npo.disabled[start] || npo.disabled[end] {
		return -1, []int{}
	}

	if start == end {
		return 0, []int{start}
	}

	visited := make(map[int]bool)
	prev := make(map[int]int)
	dist := make(map[int]int)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	for router := range npo.graph {
		dist[router] = 1<<31 - 1
	}
	dist[start] = 0

	heap.Push(&pq, &Item{
		router:   start,
		priority: 0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		u := current.router

		if u == end {
			break
		}

		if visited[u] {
			continue
		}
		visited[u] = true

		for v, latency := range npo.graph[u] {
			if npo.disabled[v] {
				continue
			}

			if alt := dist[u] + latency; alt < dist[v] {
				dist[v] = alt
				prev[v] = u
				heap.Push(&pq, &Item{
					router:   v,
					priority: alt,
				})
			}
		}
	}

	if dist[end] == 1<<31-1 {
		return -1, []int{}
	}

	path := []int{}
	for at := end; at != start; at = prev[at] {
		path = append([]int{at}, path...)
	}
	path = append([]int{start}, path...)

	return dist[end], path
}

type Item struct {
	router   int
	priority int
	index    int
}

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