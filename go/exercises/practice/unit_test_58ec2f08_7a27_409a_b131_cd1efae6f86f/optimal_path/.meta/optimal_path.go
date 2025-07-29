package optimal_path

import (
	"container/heap"
)

type Edge struct {
	to      int
	latency int
}

type cost struct {
	maxCap  int
	latency int
}

type State struct {
	node    int
	maxCap  int
	latency int
	index   int
}

// PriorityQueue implements heap.Interface for *State based on lexicographical order.
// Lex order: first by maxCap, then by latency.
type PriorityQueue []*State

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].maxCap == pq[j].maxCap {
		return pq[i].latency < pq[j].latency
	}
	return pq[i].maxCap < pq[j].maxCap
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	state := x.(*State)
	state.index = n
	*pq = append(*pq, state)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	state := old[n-1]
	state.index = -1
	*pq = old[0 : n-1]
	return state
}

// FindOptimalPath computes the optimal path from node s to node d in the network.
// The optimality criteria are defined as follows:
// 1. Minimize the maximum processing capacity encountered along the path.
// 2. Among paths with equal maximum capacity, minimize the total latency.
// If no valid path exists or if s or d are invalid indices, an empty slice is returned.
func FindOptimalPath(n int, edges [][]int, capacities []int, s int, d int) []int {
	// Validate source and destination nodes.
	if s < 0 || s >= n || d < 0 || d >= n {
		return []int{}
	}

	// Build the graph as an adjacency list.
	graph := make([][]Edge, n)
	for _, e := range edges {
		if len(e) != 3 {
			continue
		}
		u, v, lat := e[0], e[1], e[2]
		if u < 0 || u >= n || v < 0 || v >= n {
			continue
		}
		graph[u] = append(graph[u], Edge{
			to:      v,
			latency: lat,
		})
	}

	const inf = 1 << 30
	best := make([]cost, n)
	parent := make([]int, n)
	for i := 0; i < n; i++ {
		best[i] = cost{maxCap: inf, latency: inf}
		parent[i] = -1
	}

	// Initialize starting state.
	best[s] = cost{maxCap: capacities[s], latency: 0}
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &State{node: s, maxCap: capacities[s], latency: 0})

	// Dijkstra-like algorithm modified for lexicographical cost (maxCap, latency).
	for pq.Len() > 0 {
		cur := heap.Pop(pq).(*State)
		u := cur.node

		// Skip if the state is not up-to-date with the best cost found.
		if cur.maxCap != best[u].maxCap || cur.latency != best[u].latency {
			continue
		}

		// Explore all outgoing edges from node u.
		for _, edge := range graph[u] {
			v := edge.to
			newMax := cur.maxCap
			if capacities[v] > newMax {
				newMax = capacities[v]
			}
			newLatency := cur.latency + edge.latency

			// Lexicographical comparison: update if new path is better.
			if newMax < best[v].maxCap || (newMax == best[v].maxCap && newLatency < best[v].latency) {
				best[v] = cost{maxCap: newMax, latency: newLatency}
				parent[v] = u
				heap.Push(pq, &State{node: v, maxCap: newMax, latency: newLatency})
			}
		}
	}

	// If destination was never reached.
	if best[d].maxCap == inf && best[d].latency == inf {
		return []int{}
	}

	// Reconstruct the path from destination to source.
	path := []int{}
	for cur := d; cur != -1; cur = parent[cur] {
		path = append(path, cur)
	}
	// Reverse the path to get correct order from s to d.
	for i, j := 0, len(path)-1; i < j; i, j = i+1, j-1 {
		path[i], path[j] = path[j], path[i]
	}
	return path
}