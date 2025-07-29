package net_routing

import (
	"container/heap"
	"math"
)

type Network struct {
	nodes      map[int]bool
	neighbors  map[int]map[int]int
	connection map[int]map[int]bool
}

func NewNetwork() *Network {
	return &Network{
		nodes:      make(map[int]bool),
		neighbors:  make(map[int]map[int]int),
		connection: make(map[int]map[int]bool),
	}
}

func (n *Network) AddNode(id int) {
	if !n.nodes[id] {
		n.nodes[id] = true
		n.neighbors[id] = make(map[int]int)
		n.connection[id] = make(map[int]bool)
	}
}

func (n *Network) RemoveNode(id int) {
	if !n.nodes[id] {
		return
	}

	delete(n.nodes, id)

	for neighbor := range n.neighbors[id] {
		delete(n.neighbors[neighbor], id)
		delete(n.connection[neighbor], id)
	}

	delete(n.neighbors, id)
	delete(n.connection, id)
}

func (n *Network) AddConnection(node1, node2, latency int) {
	n.AddNode(node1)
	n.AddNode(node2)

	n.neighbors[node1][node2] = latency
	n.neighbors[node2][node1] = latency
	n.connection[node1][node2] = true
	n.connection[node2][node1] = true
}

func (n *Network) RemoveConnection(node1, node2 int) {
	if !n.nodes[node1] || !n.nodes[node2] {
		return
	}

	delete(n.neighbors[node1], node2)
	delete(n.neighbors[node2], node1)
	delete(n.connection[node1], node2)
	delete(n.connection[node2], node1)
}

func (n *Network) GetPath(from, to int) ([]int, int) {
	if !n.nodes[from] || !n.nodes[to] {
		return []int{}, math.MaxInt32
	}

	if from == to {
		return []int{from}, 0
	}

	visited := make(map[int]bool)
	prev := make(map[int]int)
	dist := make(map[int]int)

	for node := range n.nodes {
		dist[node] = math.MaxInt32
	}
	dist[from] = 0

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: from, priority: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item).node
		if visited[current] {
			continue
		}
		visited[current] = true

		for neighbor, latency := range n.neighbors[current] {
			if !visited[neighbor] {
				newDist := dist[current] + latency
				if newDist < dist[neighbor] {
					dist[neighbor] = newDist
					prev[neighbor] = current
					heap.Push(&pq, &Item{node: neighbor, priority: newDist})
				}
			}
		}
	}

	if dist[to] == math.MaxInt32 {
		return []int{}, math.MaxInt32
	}

	path := []int{}
	for at := to; at != from; at = prev[at] {
		path = append(path, at)
	}
	path = append(path, from)

	for i, j := 0, len(path)-1; i < j; i, j = i+1, j-1 {
		path[i], path[j] = path[j], path[i]
	}

	return path, dist[to]
}

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
	item.index = -1
	*pq = old[0 : n-1]
	return item
}