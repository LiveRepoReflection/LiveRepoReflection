package networklayout

import (
	"math"
	"sort"
)

// Solution represents a potential network layout solution
type Solution struct {
	connections    [][]int
	nodeLocations [][]int
	maxWorkload   int
	cost          int
}

// OptimalNetworkLayout returns the optimal network layout that minimizes the maximum workload
func OptimalNetworkLayout(nodes []int, latencyMatrix [][]int, maxConnections, budget, requiredConnectivity int) ([][]int, [][]int) {
	n := len(nodes)
	bestSolution := Solution{
		maxWorkload: math.MaxInt32,
	}

	// Generate all possible node location assignments
	locations := generateAllLocations(n, len(latencyMatrix))

	for _, nodeLocations := range locations {
		// Try different connection configurations for each location assignment
		solution := findBestConnections(nodes, latencyMatrix, nodeLocations, maxConnections, budget, requiredConnectivity)
		if solution.connections != nil && solution.maxWorkload < bestSolution.maxWorkload {
			bestSolution = solution
		}
	}

	return bestSolution.connections, bestSolution.nodeLocations
}

// generateAllLocations generates all possible location assignments for nodes
func generateAllLocations(nodes, locations int) [][][]int {
	var result [][][]int
	current := make([][]int, nodes)
	for i := range current {
		current[i] = []int{i, 0}
	}

	var generate func(pos int)
	generate = func(pos int) {
		if pos == nodes {
			locationsCopy := make([][]int, nodes)
			for i := range current {
				locationsCopy[i] = make([]int, 2)
				copy(locationsCopy[i], current[i])
			}
			result = append(result, locationsCopy)
			return
		}

		for loc := 0; loc < locations; loc++ {
			current[pos][1] = loc
			generate(pos + 1)
		}
	}

	generate(0)
	return result
}

// findBestConnections finds the best connection configuration for given node locations
func findBestConnections(nodes []int, latencyMatrix [][]int, nodeLocations [][]int, maxConnections, budget, requiredConnectivity int) Solution {
	n := len(nodes)
	edges := generatePossibleEdges(n)
	bestSolution := Solution{maxWorkload: math.MaxInt32}

	// Try different combinations of edges
	for mask := 0; mask < (1 << len(edges)); mask++ {
		connections := make([][]int, 0)
		cost := 0

		// Build connections based on current mask
		for i, edge := range edges {
			if (mask & (1 << i)) != 0 {
				connections = append(connections, edge)
				loc1 := nodeLocations[edge[0]][1]
				loc2 := nodeLocations[edge[1]][1]
				cost += latencyMatrix[loc1][loc2]
			}
		}

		// Validate solution
		if isValidSolution(connections, n, nodes, maxConnections, budget, cost, requiredConnectivity) {
			maxWorkload := calculateMaxWorkload(connections, nodes)
			if maxWorkload < bestSolution.maxWorkload {
				bestSolution = Solution{
					connections:    connections,
					nodeLocations: nodeLocations,
					maxWorkload:   maxWorkload,
					cost:          cost,
				}
			}
		}
	}

	return bestSolution
}

// generatePossibleEdges generates all possible edges between nodes
func generatePossibleEdges(n int) [][]int {
	var edges [][]int
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			edges = append(edges, []int{i, j})
		}
	}
	return edges
}

// isValidSolution checks if a solution meets all constraints
func isValidSolution(connections [][]int, n int, nodes []int, maxConnections, budget, cost, requiredConnectivity int) bool {
	if cost > budget {
		return false
	}

	// Check max connections constraint
	connectionCount := make(map[int]int)
	for _, conn := range connections {
		connectionCount[conn[0]]++
		connectionCount[conn[1]]++
		if connectionCount[conn[0]] > maxConnections || connectionCount[conn[1]] > maxConnections {
			return false
		}
	}

	// Check connectivity requirement
	components := findComponents(connections, n)
	return len(components) == requiredConnectivity
}

// calculateMaxWorkload calculates the maximum workload among all components
func calculateMaxWorkload(connections [][]int, nodes []int) int {
	components := findComponents(connections, len(nodes))
	maxWorkload := 0

	for _, component := range components {
		workload := 0
		for node := range component {
			workload += nodes[node]
		}
		if workload > maxWorkload {
			maxWorkload = workload
		}
	}

	return maxWorkload
}

// findComponents finds all connected components in the network
func findComponents(connections [][]int, n int) []map[int]bool {
	adj := make(map[int][]int)
	for _, conn := range connections {
		adj[conn[0]] = append(adj[conn[0]], conn[1])
		adj[conn[1]] = append(adj[conn[1]], conn[0])
	}

	visited := make([]bool, n)
	var components []map[int]bool

	for node := 0; node < n; node++ {
		if !visited[node] {
			component := make(map[int]bool)
			dfs(node, adj, visited, component)
			components = append(components, component)
		}
	}

	// Sort components by size for consistent output
	sort.Slice(components, func(i, j int) bool {
		return len(components[i]) > len(components[j])
	})

	return components
}

// dfs performs depth-first search to find connected components
func dfs(node int, adj map[int][]int, visited []bool, component map[int]bool) {
	visited[node] = true
	component[node] = true

	for _, neighbor := range adj[node] {
		if !visited[neighbor] {
			dfs(neighbor, adj, visited, component)
		}
	}
}