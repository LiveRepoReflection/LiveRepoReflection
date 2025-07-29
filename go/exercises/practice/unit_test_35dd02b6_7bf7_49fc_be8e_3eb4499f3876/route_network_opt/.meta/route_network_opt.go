package route_network_opt

import (
	"container/heap"
	"math"
	"sort"
)

// Data structures as defined in the problem specification.

type Graph struct {
	Nodes []string
	Edges []GraphEdge
}

type GraphEdge struct {
	From   string
	To     string
	Weight int
}

type Agent struct {
	ID       string
	Start    string
	Capacity int
}

type Package struct {
	ID          string
	Size        int
	Destination string
	Priority    int
}

type GraphUpdate struct {
	From      string
	To        string
	NewWeight int
}

type DeliveryInput struct {
	Graph    Graph
	Agents   []Agent
	Packages []Package
	Updates  []GraphUpdate
}

type AgentDecision struct {
	AgentID          string
	Route            []string
	PackagesDelivered []string
}

type DeliveryOutput struct {
	Decisions []AgentDecision
}

// OptimizeRoutes processes the input and returns routing decisions for each agent.
// It applies graph updates, assigns packages to agents based on capacity and priority,
// and computes routes using Dijkstra's algorithm.
func OptimizeRoutes(input *DeliveryInput) DeliveryOutput {
	// Apply graph updates to modify edge weights.
	for _, update := range input.Updates {
		for i, edge := range input.Graph.Edges {
			if edge.From == update.From && edge.To == update.To {
				input.Graph.Edges[i].Weight = update.NewWeight
			}
		}
	}

	// Build adjacency list for the graph.
	adjList := buildAdjacencyList(input.Graph)

	// Sort packages by priority (lower number means higher priority).
	sortedPackages := make([]Package, len(input.Packages))
	copy(sortedPackages, input.Packages)
	sort.Slice(sortedPackages, func(i, j int) bool {
		return sortedPackages[i].Priority < sortedPackages[j].Priority
	})

	// Use map to mark assigned packages.
	assigned := make(map[string]bool)

	decisions := []AgentDecision{}

	// For each agent, assign packages greedily if they fit within the capacity.
	for _, agent := range input.Agents {
		currentLocation := agent.Start
		totalUsed := 0
		agentDelivered := []string{}
		agentRoute := []string{currentLocation}

		// Iterate over sorted packages and assign if possible.
		for _, pkg := range sortedPackages {
			if assigned[pkg.ID] {
				continue
			}
			if totalUsed+pkg.Size > agent.Capacity {
				continue
			}
			// Compute the shortest path from currentLocation to the package destination.
			legRoute, found := dijkstra(adjList, currentLocation, pkg.Destination)
			if !found || len(legRoute) == 0 {
				continue
			}
			// Append the legRoute to agentRoute.
			// Avoid duplicating the current location.
			if len(legRoute) > 0 {
				// Remove the first node of legRoute if it's equal to currentLocation.
				if legRoute[0] == currentLocation {
					legRoute = legRoute[1:]
				}
			}
			agentRoute = append(agentRoute, legRoute...)
			totalUsed += pkg.Size
			agentDelivered = append(agentDelivered, pkg.ID)
			assigned[pkg.ID] = true
			currentLocation = pkg.Destination
		}

		decision := AgentDecision{
			AgentID:          agent.ID,
			Route:            agentRoute,
			PackagesDelivered: agentDelivered,
		}
		decisions = append(decisions, decision)
	}

	return DeliveryOutput{
		Decisions: decisions,
	}
}

// buildAdjacencyList constructs a map from node to list of outgoing edges.
func buildAdjacencyList(graph Graph) map[string][]GraphEdge {
	adj := make(map[string][]GraphEdge)
	for _, node := range graph.Nodes {
		adj[node] = []GraphEdge{}
	}
	for _, edge := range graph.Edges {
		adj[edge.From] = append(adj[edge.From], edge)
	}
	return adj
}

// dijkstra computes the shortest path from start to end using Dijkstra's algorithm.
// It returns the list of nodes in the path and a boolean indicating whether a path was found.
func dijkstra(adj map[string][]GraphEdge, start, end string) ([]string, bool) {
	// distances holds the best known distance to each node.
	distances := make(map[string]float64)
	// previous holds the previous node in the optimal path.
	previous := make(map[string]string)

	// Initialize distances to infinity.
	for node := range adj {
		distances[node] = math.Inf(1)
	}
	distances[start] = 0

	// Priority queue for nodes.
	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{
		node:     start,
		priority: 0,
	})

	for pq.Len() > 0 {
		item := heap.Pop(pq).(*Item)
		current := item.node

		// Early exit if we reached the destination.
		if current == end {
			return reconstructPath(previous, end), true
		}

		// For each neighbor, relax the edge.
		for _, edge := range adj[current] {
			alt := distances[current] + float64(edge.Weight)
			if alt < distances[edge.To] {
				distances[edge.To] = alt
				previous[edge.To] = current
				heap.Push(pq, &Item{
					node:     edge.To,
					priority: alt,
				})
			}
		}
	}

	// If end is unreachable, return false.
	if _, ok := distances[end]; !ok || distances[end] == math.Inf(1) {
		return []string{}, false
	}
	return reconstructPath(previous, end), true
}

// reconstructPath builds the path from start to end using the previous map.
func reconstructPath(previous map[string]string, end string) []string {
	var path []string
	current := end
	for {
		path = append([]string{current}, path...)
		prev, ok := previous[current]
		if !ok {
			break
		}
		current = prev
	}
	return path
}

// Item is an item in the priority queue.
type Item struct {
	node     string
	priority float64
	index    int
}

// PriorityQueue implements a min-heap for Items.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

// Less prioritizes lower priority values.
func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

// Push adds an item.
func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

// Pop removes the item with the smallest priority.
func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil  // avoid memory leak
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}