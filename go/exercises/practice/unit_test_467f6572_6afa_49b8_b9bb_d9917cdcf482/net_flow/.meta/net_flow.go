package net_flow

import (
	"container/heap"
	"math"
)

type Edge struct {
	to       int
	capacity int
	flow     int
	rev      int
}

type Graph struct {
	nodes []int
	edges [][]Edge
}

func NewGraph(n int) *Graph {
	return &Graph{
		nodes: make([]int, n),
		edges: make([][]Edge, n),
	}
}

func (g *Graph) AddEdge(from, to, capacity int) {
	g.edges[from] = append(g.edges[from], Edge{
		to:       to,
		capacity: capacity,
		flow:     0,
		rev:      len(g.edges[to]),
	})
	g.edges[to] = append(g.edges[to], Edge{
		to:       from,
		capacity: 0,
		flow:     0,
		rev:      len(g.edges[from]) - 1,
	})
}

func (g *Graph) bfsLevelGraph(source, sink int) ([]int, bool) {
	level := make([]int, len(g.nodes))
	for i := range level {
		level[i] = -1
	}
	level[source] = 0
	queue := []int{source}

	for len(queue) > 0 {
		u := queue[0]
		queue = queue[1:]

		for _, e := range g.edges[u] {
			if e.capacity > e.flow && level[e.to] < 0 {
				level[e.to] = level[u] + 1
				queue = append(queue, e.to)
			}
		}
	}

	return level, level[sink] >= 0
}

func (g *Graph) dfsBlockingFlow(u, sink, flow int, level, ptr []int) int {
	if u == sink {
		return flow
	}

	for ; ptr[u] < len(g.edges[u]); ptr[u]++ {
		e := &g.edges[u][ptr[u]]
		if e.capacity > e.flow && level[e.to] == level[u]+1 {
			if f := g.dfsBlockingFlow(e.to, sink, min(flow, e.capacity-e.flow), level, ptr); f > 0 {
				e.flow += f
				g.edges[e.to][e.rev].flow -= f
				return f
			}
		}
	}

	return 0
}

func (g *Graph) MaxFlow(source, sink int) int {
	flow := 0
	for {
		level, hasPath := g.bfsLevelGraph(source, sink)
		if !hasPath {
			break
		}

		ptr := make([]int, len(g.nodes))
		for {
			f := g.dfsBlockingFlow(source, sink, math.MaxInt, level, ptr)
			if f == 0 {
				break
			}
			flow += f
		}
	}
	return flow
}

type Request struct {
	from, to, amount int
	index            int
}

type PriorityQueue []*Request

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].amount > pq[j].amount
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Request)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func MinRejectedRequests(servers int, edges [][]int, requests [][]int) int {
	// Create priority queue of requests sorted by descending data amount
	pq := make(PriorityQueue, len(requests))
	for i, req := range requests {
		pq[i] = &Request{
			from:  req[0],
			to:    req[1],
			amount: req[2],
			index: i,
		}
	}
	heap.Init(&pq)

	// Create residual graph
	graph := NewGraph(servers)
	for _, e := range edges {
		graph.AddEdge(e[0], e[1], e[2])
	}

	rejected := 0
	tempGraph := NewGraph(servers)
	
	for pq.Len() > 0 {
		req := heap.Pop(&pq).(*Request)
		
		// Check if path exists
		tempGraph = NewGraph(servers)
		for _, e := range edges {
			tempGraph.AddEdge(e[0], e[1], e[2])
		}
		
		flow := tempGraph.MaxFlow(req.from, req.to)
		if flow < req.amount {
			rejected++
			continue
		}
		
		// If path exists with enough capacity, update the main graph
		graph.MaxFlow(req.from, req.to)
		for i := range graph.edges {
			for j := range graph.edges[i] {
				if graph.edges[i][j].flow > 0 {
					graph.edges[i][j].capacity -= graph.edges[i][j].flow
					graph.edges[i][j].flow = 0
				}
			}
		}
	}
	
	return rejected
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}