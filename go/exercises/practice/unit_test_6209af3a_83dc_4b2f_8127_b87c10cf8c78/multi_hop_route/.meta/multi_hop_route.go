package multi_hop_route

import (
	"container/heap"
	"math"
)

type edge struct {
	to       int
	latency  int
}

type node struct {
	id       int
	distance int
}

type priorityQueue []*node

func (pq priorityQueue) Len() int           { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool { return pq[i].distance < pq[j].distance }
func (pq priorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }

func (pq *priorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*node))
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[:n-1]
	return item
}

func dijkstra(graph [][]edge, start int) []int {
	n := len(graph)
	dist := make([]int, n)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[start] = 0

	pq := make(priorityQueue, 0)
	heap.Push(&pq, &node{id: start, distance: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*node)
		if current.distance > dist[current.id] {
			continue
		}

		for _, e := range graph[current.id] {
			if newDist := current.distance + e.latency; newDist < dist[e.to] {
				dist[e.to] = newDist
				heap.Push(&pq, &node{id: e.to, distance: newDist})
			}
		}
	}

	return dist
}

func FindOptimalRoute(N int, edges [][3]int, source int, destination int, intermediates []int) int {
	// Build adjacency list
	graph := make([][]edge, N)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		graph[u] = append(graph[u], edge{to: v, latency: w})
	}

	// Precompute all pairs shortest paths
	allDist := make([][]int, N)
	for i := 0; i < N; i++ {
		allDist[i] = dijkstra(graph, i)
	}

	// Check if source can reach first intermediate
	if len(intermediates) > 0 {
		if allDist[source][intermediates[0]] == math.MaxInt32 {
			return -1
		}
	}

	// Check if last intermediate can reach destination
	if len(intermediates) > 0 {
		if allDist[intermediates[len(intermediates)-1]][destination] == math.MaxInt32 {
			return -1
		}
	}

	// Check connectivity between intermediates
	for i := 0; i < len(intermediates)-1; i++ {
		if allDist[intermediates[i]][intermediates[i+1]] == math.MaxInt32 {
			return -1
		}
	}

	// Calculate total path
	total := 0
	current := source

	for _, next := range intermediates {
		total += allDist[current][next]
		if total > math.MaxInt32 {
			return -1
		}
		current = next
	}

	total += allDist[current][destination]
	if total > math.MaxInt32 {
		return -1
	}

	return total
}