package uncertain_route

import (
	"container/heap"
	"errors"
)

// Edge represents a directed edge from one node to another with associated properties.
type Edge struct {
	To          string
	Distance    float64
	TravelTime  float64
	Uncertainty float64
}

// Graph represents a directed graph using an adjacency list.
type Graph struct {
	adj map[string][]Edge
}

// NewGraph creates and returns a new Graph.
func NewGraph() *Graph {
	return &Graph{
		adj: make(map[string][]Edge),
	}
}

// AddEdge adds a directed edge from 'from' to 'to' with the provided properties.
func (g *Graph) AddEdge(from, to string, distance, travelTime, uncertainty float64) {
	edge := Edge{
		To:          to,
		Distance:    distance,
		TravelTime:  travelTime,
		Uncertainty: uncertainty,
	}
	g.adj[from] = append(g.adj[from], edge)
	// Ensure that both nodes exist in the graph.
	if _, exists := g.adj[to]; !exists {
		g.adj[to] = []Edge{}
	}
}

// UpdateEdge updates the properties of an existing directed edge from 'from' to 'to'.
// If the edge does not exist, the function does nothing.
func (g *Graph) UpdateEdge(from, to string, distance, travelTime, uncertainty float64) {
	edges, exists := g.adj[from]
	if !exists {
		return
	}
	for i := range edges {
		if edges[i].To == to {
			g.adj[from][i].Distance = distance
			g.adj[from][i].TravelTime = travelTime
			g.adj[from][i].Uncertainty = uncertainty
			return
		}
	}
}

// ErrNoRoute is returned when no valid route exists between source and destination.
var ErrNoRoute = errors.New("no route found")

// Item represents an element in the priority queue.
type Item struct {
	node  string
	cost  float64
	index int
}

// PriorityQueue implements a min-heap for Items based on their cost.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
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
	old[n-1] = nil // avoid memory leak
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

// PlanRoute calculates the optimal route from source to destination using Dijkstra's algorithm.
// The weight of each edge is determined by the risk-adjusted travel time: TravelTime * (1 + Uncertainty).
// It returns the list of node names representing the optimal path, or an error if no path exists.
func (g *Graph) PlanRoute(source, destination string) ([]string, error) {
	// Check that the source node exists.
	if _, exists := g.adj[source]; !exists {
		return nil, ErrNoRoute
	}

	// Initialize distance map and predecessor map.
	dist := make(map[string]float64)
	prev := make(map[string]string)
	const inf = 1e18
	for node := range g.adj {
		dist[node] = inf
	}
	dist[source] = 0

	// Priority queue for Dijkstra.
	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &Item{node: source, cost: 0})

	for pq.Len() > 0 {
		currentItem := heap.Pop(&pq).(*Item)
		currentNode := currentItem.node
		currentCost := currentItem.cost

		// Early exit if we reached the destination.
		if currentNode == destination {
			break
		}
		// Skip if we already found a better path.
		if currentCost > dist[currentNode] {
			continue
		}
		// Process all outgoing edges.
		for _, edge := range g.adj[currentNode] {
			// The risk-adjusted travel time.
			weight := edge.TravelTime * (1 + edge.Uncertainty)
			newCost := currentCost + weight
			if newCost < dist[edge.To] {
				dist[edge.To] = newCost
				prev[edge.To] = currentNode
				heap.Push(&pq, &Item{node: edge.To, cost: newCost})
			}
		}
	}

	if dist[destination] == inf {
		return nil, ErrNoRoute
	}

	// Reconstruct the path.
	path := []string{}
	for at := destination; at != ""; at = prev[at] {
		path = append([]string{at}, path...)
		if at == source {
			break
		}
	}

	if len(path) == 0 || path[0] != source {
		return nil, ErrNoRoute
	}
	return path, nil
}