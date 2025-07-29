package network_routing

import (
	"container/heap"
)

type Network struct {
	size     int
	adj      []map[int]int // adjacency list: node -> {neighbor: latency}
}

func NewNetwork(n int) *Network {
	adj := make([]map[int]int, n)
	for i := range adj {
		adj[i] = make(map[int]int)
	}
	return &Network{
		size: n,
		adj:  adj,
	}
}

func (n *Network) AddLink(node1, node2, latency int) {
	n.adj[node1][node2] = latency
	n.adj[node2][node1] = latency
}

func (n *Network) RemoveLink(node1, node2 int) {
	delete(n.adj[node1], node2)
	delete(n.adj[node2], node1)
}

func (n *Network) GetShortestPath(startNode, endNode int) int {
	if startNode == endNode {
		return 0
	}

	dist := make([]int, n.size)
	for i := range dist {
		dist[i] = -1
	}
	dist[startNode] = 0

	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Item{
		node:     startNode,
		priority: 0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		u := current.node

		if u == endNode {
			return dist[u]
		}

		for v, latency := range n.adj[u] {
			if dist[v] == -1 || dist[v] > dist[u]+latency {
				dist[v] = dist[u] + latency
				heap.Push(&pq, &Item{
					node:     v,
					priority: dist[v],
				})
			}
		}
	}

	return -1
}

// PriorityQueue implementation for Dijkstra's algorithm
type Item struct {
	node     int
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