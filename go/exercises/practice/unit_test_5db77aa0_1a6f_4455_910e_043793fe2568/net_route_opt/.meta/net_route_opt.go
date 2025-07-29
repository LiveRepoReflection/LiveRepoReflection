package net_route_opt

import (
	"container/heap"
	"math"
)

type Edge struct {
	to, weight int
}

func FindDisjointPaths(n int, edges [][]int, src, dest, maxLatency int) [][]int {
	// Build the graph as an adjacency list.
	graph := make([][]Edge, n)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		graph[u] = append(graph[u], Edge{v, w})
		graph[v] = append(graph[v], Edge{u, w})
	}

	var result [][]int
	removed := make([]bool, n)
	// Ensure that src and dest are never removed.
	removed[src] = false
	removed[dest] = false

	// Iteratively find a valid path meeting the maxLatency constraint and mark intermediate nodes as removed.
	for {
		path, cost := dijkstra(n, graph, src, dest, removed)
		if len(path) == 0 || cost > maxLatency {
			break
		}
		result = append(result, path)
		// Remove intermediate nodes (excluding src and dest) to maintain disjointness.
		for _, node := range path {
			if node != src && node != dest {
				removed[node] = true
			}
		}
	}
	return result
}

type Item struct {
	node  int
	dist  int
	index int
}

// PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Item

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
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// dijkstra finds the shortest path from src to dest in the graph while ignoring nodes that are marked as removed
// (except src and dest which should always be considered). It returns the path (as a slice of nodes) and the total cost.
func dijkstra(n int, graph [][]Edge, src, dest int, removed []bool) ([]int, int) {
	dist := make([]int, n)
	parent := make([]int, n)
	for i := 0; i < n; i++ {
		dist[i] = math.MaxInt32
		parent[i] = -1
	}
	dist[src] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: src, dist: 0})

	for pq.Len() > 0 {
		current := heap.Pop(pq).(*Item)
		u := current.node
		if u == dest {
			break
		}
		if current.dist > dist[u] {
			continue
		}
		// Skip u if removed (unless it's src or dest).
		if removed[u] && u != src && u != dest {
			continue
		}
		for _, edge := range graph[u] {
			v := edge.to
			// Skip neighbor if removed (unless it's src or dest).
			if removed[v] && v != src && v != dest {
				continue
			}
			alt := dist[u] + edge.weight
			if alt < dist[v] {
				dist[v] = alt
				parent[v] = u
				heap.Push(pq, &Item{node: v, dist: alt})
			}
		}
	}

	if dist[dest] == math.MaxInt32 {
		return nil, math.MaxInt32
	}

	// Reconstruct path from src to dest.
	var path []int
	for cur := dest; cur != -1; cur = parent[cur] {
		path = append(path, cur)
	}
	// Reverse the path.
	for i, j := 0, len(path)-1; i < j; i, j = i+1, j-1 {
		path[i], path[j] = path[j], path[i]
	}
	return path, dist[dest]
}