package optimal_evac

import (
	"container/heap"
	"math"
	"sort"
)

type Edge struct {
	to, weight int
}

type Item struct {
	node, dist int
}

type PriorityQueue []Item

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].dist < pq[j].dist
}
func (pq PriorityQueue) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(Item))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func OptimalEvacuationTime(n int, edges [][]int, population []int, evacuationCenters []int, maxRoadCapacity int) float64 {
	// Build undirected graph representation.
	graph := make([][]Edge, n)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		graph[u] = append(graph[u], Edge{to: v, weight: w})
		graph[v] = append(graph[v], Edge{to: u, weight: w})
	}

	const INF = math.MaxInt64
	d := make([]int, n)
	count := make([]float64, n)
	for i := 0; i < n; i++ {
		d[i] = INF
	}

	// Multi-source Dijkstra initialization.
	pq := &PriorityQueue{}
	isCenter := make([]bool, n)
	for _, center := range evacuationCenters {
		d[center] = 0
		count[center] = 1.0
		isCenter[center] = true
		heap.Push(pq, Item{node: center, dist: 0})
	}

	// Multi-source Dijkstra to calculate shortest distances and count of shortest paths.
	for pq.Len() > 0 {
		item := heap.Pop(pq).(Item)
		u := item.node
		if item.dist != d[u] {
			continue
		}
		for _, edge := range graph[u] {
			v := edge.to
			newDist := d[u] + edge.weight
			if newDist < d[v] {
				d[v] = newDist
				count[v] = count[u]
				heap.Push(pq, Item{node: v, dist: newDist})
			} else if newDist == d[v] {
				count[v] += count[u]
			}
		}
	}

	// Check if any node with population > 0 is unreachable.
	for i := 0; i < n; i++ {
		if population[i] > 0 && d[i] == INF {
			return -1
		}
	}

	// Build DAG: for every edge (u, v), if d[u] == d[v] + w, then add a directed edge u -> v.
	dag := make([][]int, n)
	for u := 0; u < n; u++ {
		for _, edge := range graph[u] {
			v := edge.to
			if d[u] == d[v]+edge.weight {
				dag[u] = append(dag[u], v)
			}
		}
	}

	// Compute flows along the DAG.
	// Each node starts with its population flow.
	f := make([]float64, n)
	for i := 0; i < n; i++ {
		f[i] = float64(population[i])
	}

	// Create list of nodes sorted in descending order of distance.
	nodes := make([]int, n)
	for i := 0; i < n; i++ {
		nodes[i] = i
	}
	sort.Slice(nodes, func(i, j int) bool {
		return d[nodes[i]] > d[nodes[j]]
	})

	// Propagate flows from nodes further away to nodes closer (towards the evacuation centers).
	for _, u := range nodes {
		// If node is not a center and has no outgoing edge in the DAG while having population,
		// then there is no valid route.
		if len(dag[u]) == 0 {
			if !isCenter[u] && f[u] > 0 {
				return -1
			}
			continue
		}

		// Sum the counts for all valid outgoing edges.
		var total float64 = 0
		for _, v := range dag[u] {
			total += count[v]
		}
		if total == 0 {
			if f[u] > 0 {
				return -1
			}
			continue
		}

		// Distribute flow proportionally along each outgoing edge.
		for _, v := range dag[u] {
			flow := f[u] * (count[v] / total)
			if flow > float64(maxRoadCapacity) {
				return -1
			}
			f[v] += flow
		}
	}

	// The maximum evacuation time is the maximum shortest distance among nodes with population > 0.
	maxTime := 0
	for i := 0; i < n; i++ {
		if population[i] > 0 && d[i] > maxTime {
			maxTime = d[i]
		}
	}

	return float64(maxTime)
}