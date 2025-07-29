package networkroute

import (
	"container/heap"
	"math"
)

type Edge struct {
	node     int
	latency  int
	bandwidth int
}

type Path struct {
	nodes     []int
	bandwidth int
	latency   int
}

type PriorityQueueItem struct {
	node      int
	bandwidth int
	latency   int
	path      []int
	index     int
}

type PriorityQueue []*PriorityQueueItem

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].bandwidth == pq[j].bandwidth {
		return pq[i].latency < pq[j].latency
	}
	return pq[i].bandwidth > pq[j].bandwidth
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

func FindOptimalPath(nodes []int, edges [][4]int, source int, destination int, minBandwidth int, maxLatency int) []int {
	if source == destination {
		return []int{source}
	}

	graph := make(map[int][]Edge)
	for _, edge := range edges {
		from, to, latency, bandwidth := edge[0], edge[1], edge[2], edge[3]
		graph[from] = append(graph[from], Edge{to, latency, bandwidth})
		graph[to] = append(graph[to], Edge{from, latency, bandwidth})
	}

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &PriorityQueueItem{
		node:      source,
		bandwidth: math.MaxInt32,
		latency:   0,
		path:      []int{source},
	})

	visited := make(map[int]struct{})
	bestPaths := make(map[int]Path)

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*PriorityQueueItem)

		if _, exists := visited[current.node]; exists {
			continue
		}
		visited[current.node] = struct{}{}

		if current.node == destination {
			if current.bandwidth >= minBandwidth && current.latency <= maxLatency {
				return current.path
			}
			continue
		}

		for _, edge := range graph[current.node] {
			if _, exists := visited[edge.node]; exists {
				continue
			}

			newBandwidth := min(current.bandwidth, edge.bandwidth)
			newLatency := current.latency + edge.latency

			if newLatency > maxLatency {
				continue
			}

			if existing, exists := bestPaths[edge.node]; exists {
				if existing.bandwidth > newBandwidth || (existing.bandwidth == newBandwidth && existing.latency <= newLatency) {
					continue
				}
			}

			newPath := make([]int, len(current.path))
			copy(newPath, current.path)
			newPath = append(newPath, edge.node)

			bestPaths[edge.node] = Path{
				nodes:     newPath,
				bandwidth: newBandwidth,
				latency:   newLatency,
			}

			heap.Push(&pq, &PriorityQueueItem{
				node:      edge.node,
				bandwidth: newBandwidth,
				latency:   newLatency,
				path:      newPath,
			})
		}
	}

	return []int{}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}