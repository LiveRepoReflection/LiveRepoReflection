package airport_placement

import (
	"container/heap"
	"math"
)

type Node struct {
	id    int
	dist  int
	index int
}

type PriorityQueue []*Node

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].dist < pq[j].dist
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	node := x.(*Node)
	node.index = n
	*pq = append(*pq, node)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	node := old[n-1]
	old[n-1] = nil
	node.index = -1
	*pq = old[0 : n-1]
	return node
}

func OptimalAirportPlacement(n int, edges [][]int) int {
	if n == 1 {
		return 0
	}

	// Build adjacency list
	adj := make([][][2]int, n)
	for _, edge := range edges {
		u, v, w := edge[0], edge[1], edge[2]
		adj[u] = append(adj[u], [2]int{v, w})
		adj[v] = append(adj[v], [2]int{u, w})
	}

	minMaxDist := math.MaxInt32
	bestNode := 0

	for start := 0; start < n; start++ {
		// Dijkstra's algorithm
		dist := make([]int, n)
		for i := range dist {
			dist[i] = math.MaxInt32
		}
		dist[start] = 0

		pq := make(PriorityQueue, 0)
		heap.Push(&pq, &Node{id: start, dist: 0})

		for pq.Len() > 0 {
			current := heap.Pop(&pq).(*Node)
			u := current.id

			if current.dist > dist[u] {
				continue
			}

			for _, neighbor := range adj[u] {
				v, w := neighbor[0], neighbor[1]
				if dist[v] > dist[u]+w {
					dist[v] = dist[u] + w
					heap.Push(&pq, &Node{id: v, dist: dist[v]})
				}
			}
		}

		// Find maximum distance for this start node
		maxDist := 0
		for _, d := range dist {
			if d > maxDist {
				maxDist = d
			}
		}

		// Update best node if this one is better
		if maxDist < minMaxDist || (maxDist == minMaxDist && start < bestNode) {
			minMaxDist = maxDist
			bestNode = start
		}
	}

	return bestNode
}