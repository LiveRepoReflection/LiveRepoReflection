package net_route

import (
	"container/heap"
	"math"
)

type Network struct {
	n      int
	adj    []map[int]int
	failed []bool
}

func NewNetwork(n int) *Network {
	adj := make([]map[int]int, n)
	for i := 0; i < n; i++ {
		adj[i] = make(map[int]int)
	}
	failed := make([]bool, n)
	return &Network{n: n, adj: adj, failed: failed}
}

func (net *Network) AddLink(u, v, latency int) {
	if u < 0 || u >= net.n || v < 0 || v >= net.n {
		return
	}
	// Do not add link if either node is failed.
	if net.failed[u] || net.failed[v] {
		return
	}
	net.adj[u][v] = latency
	net.adj[v][u] = latency
}

func (net *Network) RemoveLink(u, v int) {
	if u < 0 || u >= net.n || v < 0 || v >= net.n {
		return
	}
	delete(net.adj[u], v)
	delete(net.adj[v], u)
}

func (net *Network) NodeFailure(node int) {
	if node < 0 || node >= net.n {
		return
	}
	if net.failed[node] {
		return
	}
	net.failed[node] = true
	// Remove all links from the failed node and from its neighbors.
	for neighbor := range net.adj[node] {
		delete(net.adj[neighbor], node)
	}
	net.adj[node] = make(map[int]int)
}

func (net *Network) RouteRequest(source, destination int) int {
	// Check for invalid indices or failed nodes.
	if source < 0 || source >= net.n || destination < 0 || destination >= net.n {
		return -1
	}
	if net.failed[source] || net.failed[destination] {
		return -1
	}
	if source == destination {
		return 0
	}

	// Dijkstra's algorithm
	dist := make([]int, net.n)
	for i := 0; i < net.n; i++ {
		dist[i] = math.MaxInt64
	}
	dist[source] = 0

	visited := make([]bool, net.n)
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{node: source, cost: 0})

	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		u := item.node
		if visited[u] {
			continue
		}
		visited[u] = true

		if u == destination {
			return item.cost
		}

		// Iterate through the neighbors of node u.
		for v, weight := range net.adj[u] {
			// Skip if neighbor is failed or already visited.
			if net.failed[v] {
				continue
			}
			if visited[v] {
				continue
			}
			newCost := item.cost + weight
			if newCost < dist[v] {
				dist[v] = newCost
				heap.Push(pq, &Item{node: v, cost: newCost})
			}
		}
	}
	return -1
}

type Item struct {
	node int
	cost int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}
func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*Item))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}