package net_optimize

import (
	"container/heap"
	"math"
)

type Edge struct {
	node   int
	weight int
}

type Graph struct {
	nodes     int
	edges     map[int][]Edge
	critical  map[int]bool
	penalty   int
}

type Item struct {
	node     int
	distance int
	hops     int
	index    int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].distance < pq[j].distance
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

func NewGraph(n int, connections [][]int, criticalNodes []int, penalty int) *Graph {
	g := &Graph{
		nodes:    n,
		edges:    make(map[int][]Edge),
		critical: make(map[int]bool),
		penalty:  penalty,
	}

	for _, node := range criticalNodes {
		g.critical[node] = true
	}

	for _, conn := range connections {
		from, to, weight := conn[0], conn[1], conn[2]
		g.edges[from] = append(g.edges[from], Edge{to, weight})
		g.edges[to] = append(g.edges[to], Edge{from, weight})
	}

	return g
}

func (g *Graph) shortestPath(start, end, maxHops int) int {
	distances := make([]int, g.nodes)
	hops := make([]int, g.nodes)
	for i := range distances {
		distances[i] = math.MaxInt32
		hops[i] = math.MaxInt32
	}
	distances[start] = 0
	hops[start] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Item{
		node:     start,
		distance: 0,
		hops:     0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		if current.node == end {
			return current.distance
		}

		if current.hops >= maxHops {
			continue
		}

		for _, edge := range g.edges[current.node] {
			newDistance := current.distance + edge.weight
			newHops := current.hops + 1

			if g.critical[edge.node] {
				newDistance += g.penalty
			}

			if newDistance < distances[edge.node] || (newDistance == distances[edge.node] && newHops < hops[edge.node]) {
				distances[edge.node] = newDistance
				hops[edge.node] = newHops
				heap.Push(&pq, &Item{
					node:     edge.node,
					distance: newDistance,
					hops:     newHops,
				})
			}
		}
	}

	return -1
}

func OptimizeNetwork(n int, connections [][]int, queries [][]int, criticalNodes []int, criticalNodePenalty int, maxHops int) []int {
	g := NewGraph(n, connections, criticalNodes, criticalNodePenalty)
	results := make([]int, len(queries))

	for i, query := range queries {
		start, end := query[0], query[1]
		results[i] = g.shortestPath(start, end, maxHops)
	}

	return results
}