package meeting_point

import (
	"container/heap"
	"math"
)

// Edge represents an edge in the graph with a destination node and weight.
type Edge struct {
	to     int
	weight int
}

// MeetingPoint finds the optimal meeting point in the graph such that the maximum distance
// any friend must travel is minimized. In the event of ties, the smallest index is returned.
func MeetingPoint(n int, edges [][]int, friends []int) int {
	// Build the graph as an adjacency list.
	graph := make([][]Edge, n)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		graph[u] = append(graph[u], Edge{to: v, weight: w})
		graph[v] = append(graph[v], Edge{to: u, weight: w})
	}

	// Compute shortest paths from each friend's starting node.
	friendDistances := make([][]int, len(friends))
	for i, start := range friends {
		friendDistances[i] = dijkstra(n, graph, start)
	}

	optimalNode := -1
	optimalMax := math.MaxInt64

	// For each node, determine the maximum distance any friend has to travel.
	for node := 0; node < n; node++ {
		currentMax := 0
		for i := 0; i < len(friends); i++ {
			d := friendDistances[i][node]
			if d > currentMax {
				currentMax = d
			}
		}
		// Update the optimal meeting point if a lower maximum distance is found.
		if currentMax < optimalMax {
			optimalMax = currentMax
			optimalNode = node
		}
	}
	return optimalNode
}

// dijkstra computes the shortest distances from a starting node to all other nodes
// using Dijkstra's algorithm.
func dijkstra(n int, graph [][]Edge, start int) []int {
	dist := make([]int, n)
	for i := 0; i < n; i++ {
		dist[i] = math.MaxInt64
	}
	dist[start] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{
		node: start,
		cost: 0,
	})

	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		current := item.node
		currentCost := item.cost
		// Ignore stale entries.
		if currentCost > dist[current] {
			continue
		}
		// Explore neighbors.
		for _, edge := range graph[current] {
			newCost := currentCost + edge.weight
			if newCost < dist[edge.to] {
				dist[edge.to] = newCost
				heap.Push(pq, &Item{
					node: edge.to,
					cost: newCost,
				})
			}
		}
	}
	return dist
}

// Item represents a node with a current cost for the priority queue.
type Item struct {
	node int
	cost int
}

// PriorityQueue implements heap.Interface for *Item.
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