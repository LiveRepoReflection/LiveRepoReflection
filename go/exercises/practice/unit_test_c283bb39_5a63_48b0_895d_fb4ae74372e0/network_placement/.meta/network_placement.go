package networkplacement

import (
	"container/heap"
	"math"
	"sort"
)

// Edge represents a connection between two data centers
type Edge struct {
	From    int
	To      int
	Latency int
}

// OptimalNetworkPlacement determines the optimal placement of k routers
// to minimize the total weighted latency
func OptimalNetworkPlacement(
	nodes int,
	edges []Edge,
	demand [][]int,
	routersCount int,
	routerCapacity int,
	reductionFactor float64,
) []int {
	// Handle edge cases
	if nodes == 0 || routersCount == 0 {
		return []int{}
	}

	// Limit routers count to the number of nodes
	if routersCount > nodes {
		routersCount = nodes
	}

	// Build the graph representation
	graph := buildGraph(nodes, edges)

	// Try all possible router combinations using combinatorial search
	bestPlacement := []int{}
	minTotalLatency := math.MaxInt32

	// Start with a greedy solution to set an initial benchmark
	greedyPlacement := findGreedyPlacement(nodes, graph, demand, routersCount, routerCapacity, reductionFactor)
	if len(greedyPlacement) > 0 {
		greedyLatency := calculateTotalWeightedLatencyWithCapacity(
			greedyPlacement, nodes, graph, demand, routerCapacity, reductionFactor)
		if greedyLatency < minTotalLatency {
			minTotalLatency = greedyLatency
			bestPlacement = make([]int, len(greedyPlacement))
			copy(bestPlacement, greedyPlacement)
		}
	}

	// Use a combinatorial search to find the optimal solution
	currentPlacement := make([]int, 0, routersCount)
	combinatorialSearch(
		0, nodes, routersCount, currentPlacement, graph, demand,
		routerCapacity, reductionFactor, &bestPlacement, &minTotalLatency)

	// Sort the result for consistency
	sort.Ints(bestPlacement)
	return bestPlacement
}

// buildGraph creates an adjacency list representation of the network
func buildGraph(nodes int, edges []Edge) [][]Edge {
	adjacencyList := make([][]Edge, nodes)
	for _, edge := range edges {
		// Add edge in both directions (undirected graph)
		adjacencyList[edge.From] = append(adjacencyList[edge.From], Edge{
			From:    edge.From,
			To:      edge.To,
			Latency: edge.Latency,
		})
		adjacencyList[edge.To] = append(adjacencyList[edge.To], Edge{
			From:    edge.To,
			To:      edge.From,
			Latency: edge.Latency,
		})
	}
	return adjacencyList
}

// combinatorialSearch recursively explores all possible router placements
func combinatorialSearch(
	start, nodes, remainingRouters int,
	currentPlacement []int,
	graph [][]Edge,
	demand [][]int,
	routerCapacity int,
	reductionFactor float64,
	bestPlacement *[]int,
	minTotalLatency *int,
) {
	// Base case: all routers have been placed
	if remainingRouters == 0 {
		latency := calculateTotalWeightedLatencyWithCapacity(
			currentPlacement, nodes, graph, demand, routerCapacity, reductionFactor)
		if latency < *minTotalLatency {
			*minTotalLatency = latency
			*bestPlacement = make([]int, len(currentPlacement))
			copy(*bestPlacement, currentPlacement)
		}
		return
	}

	// Try placing the current router at each possible node
	for i := start; i < nodes; i++ {
		// Add current node to the placement
		currentPlacement = append(currentPlacement, i)

		// Recursively place the remaining routers
		combinatorialSearch(
			i+1, nodes, remainingRouters-1,
			currentPlacement, graph, demand,
			routerCapacity, reductionFactor,
			bestPlacement, minTotalLatency)

		// Backtrack
		currentPlacement = currentPlacement[:len(currentPlacement)-1]
	}
}

// findGreedyPlacement tries to find a good initial placement using a greedy approach
func findGreedyPlacement(
	nodes int,
	graph [][]Edge,
	demand [][]int,
	routersCount int,
	routerCapacity int,
	reductionFactor float64,
) []int {
	// Calculate the traffic importance of each node
	nodeImportance := make([]struct {
		NodeID     int
		Importance int
	}, nodes)

	for i := 0; i < nodes; i++ {
		var totalDemand int
		for j := 0; j < nodes; j++ {
			if i != j {
				totalDemand += demand[i][j] + demand[j][i]
			}
		}
		nodeImportance[i] = struct {
			NodeID     int
			Importance int
		}{i, totalDemand}
	}

	// Sort nodes by importance (highest first)
	sort.Slice(nodeImportance, func(i, j int) bool {
		return nodeImportance[i].Importance > nodeImportance[j].Importance
	})

	// Place routers at the most important nodes
	placement := make([]int, 0, routersCount)
	for i := 0; i < routersCount && i < len(nodeImportance); i++ {
		placement = append(placement, nodeImportance[i].NodeID)
	}

	// Verify if the placement is valid (respects capacity constraints)
	if !isValidPlacement(placement, nodes, graph, demand, routerCapacity, reductionFactor) {
		return []int{} // No valid solution found with greedy approach
	}

	return placement
}

// isValidPlacement checks if a router placement satisfies capacity constraints
func isValidPlacement(
	placement []int,
	nodes int,
	graph [][]Edge,
	demand [][]int,
	routerCapacity int,
	reductionFactor float64,
) bool {
	// Create a map for quick lookup of router placements
	routerMap := make(map[int]bool)
	for _, node := range placement {
		routerMap[node] = true
	}

	// Track the load on each router
	routerLoad := make(map[int]int)
	for i := 0; i < nodes; i++ {
		for j := 0; j < nodes; j++ {
			if i == j || demand[i][j] == 0 {
				continue
			}

			// Find the shortest path between i and j
			path, _ := findShortestPath(i, j, nodes, graph, routerMap, reductionFactor)

			// Track load on each router along the path
			for _, node := range path {
				if routerMap[node] {
					routerLoad[node] += demand[i][j]
					if routerLoad[node] > routerCapacity {
						return false // Capacity exceeded
					}
				}
			}
		}
	}

	return true
}

// calculateTotalWeightedLatencyWithCapacity calculates the weighted latency with capacity checks
func calculateTotalWeightedLatencyWithCapacity(
	placement []int,
	nodes int,
	graph [][]Edge,
	demand [][]int,
	routerCapacity int,
	reductionFactor float64,
) int {
	// If the placement is not valid, return maximum latency
	if !isValidPlacement(placement, nodes, graph, demand, routerCapacity, reductionFactor) {
		return math.MaxInt32
	}

	// Create a map for quick lookup of router placements
	routerMap := make(map[int]bool)
	for _, node := range placement {
		routerMap[node] = true
	}

	totalLatency := 0
	for i := 0; i < nodes; i++ {
		for j := 0; j < nodes; j++ {
			if i == j || demand[i][j] == 0 {
				continue
			}

			// Find the shortest path latency with router placement
			_, pathLatency := findShortestPath(i, j, nodes, graph, routerMap, reductionFactor)
			totalLatency += demand[i][j] * pathLatency
		}
	}

	return totalLatency
}

// PathNode represents a node in a path
type PathNode struct {
	NodeID   int
	Distance int
	Index    int // For priority queue
}

// PriorityQueue implements a min-heap of PathNodes based on distance
type PriorityQueue []*PathNode

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Distance < pq[j].Distance
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].Index = i
	pq[j].Index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	node := x.(*PathNode)
	node.Index = n
	*pq = append(*pq, node)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	node := old[n-1]
	old[n-1] = nil       // avoid memory leak
	node.Index = -1      // for safety
	*pq = old[0 : n-1]
	return node
}

// findShortestPath uses Dijkstra's algorithm to find the shortest path
// and its latency between two nodes considering router placements
func findShortestPath(
	start, end int,
	nodes int,
	graph [][]Edge,
	routerMap map[int]bool,
	reductionFactor float64,
) ([]int, int) {
	// Initialize distances
	dist := make([]int, nodes)
	prev := make([]int, nodes)
	for i := range dist {
		dist[i] = math.MaxInt32
		prev[i] = -1
	}
	dist[start] = 0

	// Initialize priority queue
	pq := make(PriorityQueue, 0)
	nodeMap := make(map[int]*PathNode)
	startNode := &PathNode{NodeID: start, Distance: 0}
	heap.Push(&pq, startNode)
	nodeMap[start] = startNode

	// Dijkstra's algorithm
	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*PathNode)
		currentID := current.NodeID

		// If we've reached the destination, we can stop
		if currentID == end {
			break
		}

		// Skip if we've found a better path already
		if current.Distance > dist[currentID] {
			continue
		}

		// Explore neighbors
		for _, edge := range graph[currentID] {
			neighbor := edge.To
			
			// Calculate latency based on router placement
			edgeLatency := edge.Latency
			if routerMap[currentID] || routerMap[neighbor] {
				edgeLatency = int(float64(edgeLatency) * reductionFactor)
			}
			
			newDist := dist[currentID] + edgeLatency

			// If we found a shorter path
			if newDist < dist[neighbor] {
				dist[neighbor] = newDist
				prev[neighbor] = currentID

				// Update priority queue
				if node, exists := nodeMap[neighbor]; exists {
					node.Distance = newDist
					heap.Fix(&pq, node.Index)
				} else {
					node := &PathNode{NodeID: neighbor, Distance: newDist}
					heap.Push(&pq, node)
					nodeMap[neighbor] = node
				}
			}
		}
	}

	// Reconstruct the path
	if dist[end] == math.MaxInt32 {
		return nil, math.MaxInt32 // No path found
	}

	path := []int{}
	for at := end; at != -1; at = prev[at] {
		path = append([]int{at}, path...)
	}

	return path, dist[end]
}