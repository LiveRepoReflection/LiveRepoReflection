package networkplacement

import "fmt"

// Helper function for visualization and debugging
func VisualizeNetwork(nodes int, edges []Edge, routerPlacement []int) string {
	result := fmt.Sprintf("Network with %d nodes and %d routers\n", nodes, len(routerPlacement))
	
	// Create a map for quick lookup of router placements
	routerMap := make(map[int]bool)
	for _, node := range routerPlacement {
		routerMap[node] = true
	}
	
	// Print nodes
	result += "Nodes: "
	for i := 0; i < nodes; i++ {
		if routerMap[i] {
			result += fmt.Sprintf("%d[R] ", i)
		} else {
			result += fmt.Sprintf("%d ", i)
		}
	}
	result += "\n"
	
	// Print edges
	result += "Edges:\n"
	for _, edge := range edges {
		result += fmt.Sprintf("  %d -- %d (latency: %d)\n", edge.From, edge.To, edge.Latency)
	}
	
	return result
}

// Helper function to calculate traffic passing through each node
func CalculateNodeTraffic(nodes int, graph [][]Edge, demand [][]int) map[int]int {
	nodeTraffic := make(map[int]int)
	
	// Initialize traffic counts
	for i := 0; i < nodes; i++ {
		nodeTraffic[i] = 0
	}
	
	// Calculate traffic through each node
	for i := 0; i < nodes; i++ {
		for j := 0; j < nodes; j++ {
			if i == j || demand[i][j] == 0 {
				continue
			}
			
			// Find the shortest path (without routers)
			path, _ := findShortestPath(i, j, nodes, graph, make(map[int]bool), 1.0)
			
			// Add traffic to all nodes in the path
			for _, node := range path {
				nodeTraffic[node] += demand[i][j]
			}
		}
	}
	
	return nodeTraffic
}

// Helper to evaluate a specific router placement
func EvaluatePlacement(
	placement []int,
	nodes int,
	edges []Edge,
	demand [][]int,
	routerCapacity int,
	reductionFactor float64,
) (int, bool) {
	graph := buildGraph(nodes, edges)
	
	// Check if placement is valid (respects capacity constraints)
	if !isValidPlacement(placement, nodes, graph, demand, routerCapacity, reductionFactor) {
		return -1, false
	}
	
	// Calculate the total weighted latency
	latency := calculateTotalWeightedLatencyWithCapacity(
		placement, nodes, graph, demand, routerCapacity, reductionFactor)
	
	return latency, true
}