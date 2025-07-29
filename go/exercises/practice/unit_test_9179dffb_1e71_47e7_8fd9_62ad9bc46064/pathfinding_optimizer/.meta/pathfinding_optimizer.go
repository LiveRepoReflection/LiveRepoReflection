package pathfinding

import (
	"container/heap"
	"math"
)

type Edge struct {
	dest int
	cost int
}

type Graph struct {
	n      int
	adj    [][]Edge
	costs  map[int]map[int][]TimedCost // From -> To -> []TimedCost
}

type TimedCost struct {
	cost int
	time int
}

type PathfindingOptimizer struct {
	graph *Graph
}

// For Dijkstra's algorithm
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

func Initialize(n int, edges [][3]int) *PathfindingOptimizer {
	graph := &Graph{
		n:     n,
		adj:   make([][]Edge, n),
		costs: make(map[int]map[int][]TimedCost),
	}

	// Initialize the costs map
	for i := 0; i < n; i++ {
		graph.costs[i] = make(map[int][]TimedCost)
	}

	// Add initial edges
	for _, edge := range edges {
		from, to, cost := edge[0], edge[1], edge[2]
		graph.adj[from] = append(graph.adj[from], Edge{dest: to, cost: cost})
		if graph.costs[from][to] == nil {
			graph.costs[from][to] = []TimedCost{}
		}
		graph.costs[from][to] = append(graph.costs[from][to], TimedCost{cost: cost, time: 0})
	}

	return &PathfindingOptimizer{graph: graph}
}

func (po *PathfindingOptimizer) UpdateEdgeCost(source int, destination int, newCost int) {
	// Update adjacency list if needed
	found := false
	for i, edge := range po.graph.adj[source] {
		if edge.dest == destination {
			po.graph.adj[source][i].cost = newCost
			found = true
			break
		}
	}
	if !found {
		po.graph.adj[source] = append(po.graph.adj[source], Edge{dest: destination, cost: newCost})
	}

	// Update costs map
	if po.graph.costs[source][destination] == nil {
		po.graph.costs[source][destination] = []TimedCost{}
	}
	po.graph.costs[source][destination] = append(po.graph.costs[source][destination], 
		TimedCost{cost: newCost, time: 0})
}

func (po *PathfindingOptimizer) getEdgeCost(from, to int, time int) int {
	costs := po.graph.costs[from][to]
	if len(costs) == 0 {
		return math.MaxInt32
	}

	// Find the most recent cost update before or at the given time
	latestCost := costs[0].cost
	for _, tc := range costs {
		if tc.time <= time {
			latestCost = tc.cost
		} else {
			break
		}
	}
	return latestCost
}

func (po *PathfindingOptimizer) findShortestPath(start, end, deadline int) int {
	dist := make([]int, po.graph.n)
	for i := range dist {
		dist[i] = math.MaxInt32
	}
	dist[start] = 0

	pq := make(PriorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &Item{node: start, priority: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*Item)
		if current.node == end {
			return current.priority
		}

		if current.priority > dist[current.node] {
			continue
		}

		for _, edge := range po.graph.adj[current.node] {
			cost := po.getEdgeCost(current.node, edge.dest, deadline)
			if cost == math.MaxInt32 {
				continue
			}

			newDist := dist[current.node] + cost
			if newDist < dist[edge.dest] {
				dist[edge.dest] = newDist
				heap.Push(&pq, &Item{node: edge.dest, priority: newDist})
			}
		}
	}

	return math.MaxInt32
}

func (po *PathfindingOptimizer) ProcessDeliveryRequests(requests [][4]int) []int {
	result := make([]int, len(requests))

	for i, req := range requests {
		start, end, deadline, penalty := req[0], req[1], req[2], req[3]
		
		// Find shortest path
		cost := po.findShortestPath(start, end, deadline)
		
		// If path exists and meets deadline
		if cost != math.MaxInt32 && cost <= deadline {
			result[i] = cost
		} else {
			result[i] = penalty
		}
	}

	return result
}