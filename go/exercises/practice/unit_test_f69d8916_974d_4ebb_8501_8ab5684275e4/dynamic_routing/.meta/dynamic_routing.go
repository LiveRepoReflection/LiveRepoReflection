package dynamic_routing

import (
	"container/heap"
	"math"
)

type Edge struct {
	node   int
	weight int
}

type RoutingSystem struct {
	graph    map[int][]Edge
	nodeCount int
}

func NewRoutingSystem(nodeCount int, edges [][3]int) *RoutingSystem {
	rs := &RoutingSystem{
		graph:    make(map[int][]Edge),
		nodeCount: nodeCount,
	}

	for _, edge := range edges {
		u, v, weight := edge[0], edge[1], edge[2]
		rs.graph[u] = append(rs.graph[u], Edge{v, weight})
		rs.graph[v] = append(rs.graph[v], Edge{u, weight})
	}

	return rs
}

func (rs *RoutingSystem) UpdateLatency(u, v, newLatency int) {
	// Update all edges between u and v
	for i, edge := range rs.graph[u] {
		if edge.node == v {
			rs.graph[u][i].weight = newLatency
		}
	}
	for i, edge := range rs.graph[v] {
		if edge.node == u {
			rs.graph[v][i].weight = newLatency
		}
	}
}

func (rs *RoutingSystem) Route(start, end int) int {
	if start == end {
		return 0
	}

	dist := make([]int, rs.nodeCount+1)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[start] = 0

	h := &PriorityQueue{}
	heap.Init(h)
	heap.Push(h, &Item{node: start, priority: 0})

	for h.Len() > 0 {
		item := heap.Pop(h).(*Item)
		u := item.node

		if u == end {
			return dist[u]
		}

		if dist[u] < item.priority {
			continue
		}

		for _, edge := range rs.graph[u] {
			v := edge.node
			weight := edge.weight

			if dist[v] > dist[u]+weight {
				dist[v] = dist[u] + weight
				heap.Push(h, &Item{node: v, priority: dist[v]})
			}
		}
	}

	return -1
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
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}