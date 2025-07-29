package networklayout

import (
	"testing"
)

func validateSolution(t *testing.T, tc testCase, connections [][]int, nodeLocations [][]int) bool {
	// Check if node locations are valid
	if len(nodeLocations) != len(tc.nodes) {
		t.Errorf("Invalid number of node locations. Expected %d, got %d", len(tc.nodes), len(nodeLocations))
		return false
	}

	// Check if all locations are within bounds
	for _, loc := range nodeLocations {
		if loc[0] < 0 || loc[0] >= len(tc.nodes) || loc[1] < 0 || loc[1] >= len(tc.latencyMatrix) {
			t.Errorf("Invalid location indices: [%d, %d]", loc[0], loc[1])
			return false
		}
	}

	// Check connections validity
	connectionCount := make(map[int]int)
	totalCost := 0

	for _, conn := range connections {
		if conn[0] < 0 || conn[0] >= len(tc.nodes) || conn[1] < 0 || conn[1] >= len(tc.nodes) {
			t.Errorf("Invalid connection indices: [%d, %d]", conn[0], conn[1])
			return false
		}

		// Count connections per node
		connectionCount[conn[0]]++
		connectionCount[conn[1]]++

		// Calculate cost
		loc1 := nodeLocations[conn[0]][1]
		loc2 := nodeLocations[conn[1]][1]
		totalCost += tc.latencyMatrix[loc1][loc2]
	}

	// Check max connections constraint
	for node, count := range connectionCount {
		if count > tc.maxConnections {
			t.Errorf("Node %d exceeds maximum connections. Got %d, maximum allowed %d", 
				node, count, tc.maxConnections)
			return false
		}
	}

	// Check budget constraint
	if totalCost > tc.budget {
		t.Errorf("Solution exceeds budget. Cost: %d, Budget: %d", totalCost, tc.budget)
		return false
	}

	// Check connectivity requirement
	components := findConnectedComponents(connections, len(tc.nodes))
	if len(components) != tc.requiredConnectivity {
		t.Errorf("Invalid number of connected components. Expected %d, got %d", 
			tc.requiredConnectivity, len(components))
		return false
	}

	// Calculate maximum workload
	maxWorkload := 0
	for _, component := range components {
		workload := 0
		for node := range component {
			workload += tc.nodes[node]
		}
		if workload > maxWorkload {
			maxWorkload = workload
		}
	}

	if maxWorkload > tc.expectedMaxWorkload {
		t.Errorf("Solution's maximum workload %d exceeds expected maximum workload %d", 
			maxWorkload, tc.expectedMaxWorkload)
		return false
	}

	return true
}

func findConnectedComponents(connections [][]int, n int) []map[int]bool {
	visited := make([]bool, n)
	components := []map[int]bool{}

	// Build adjacency list
	adj := make(map[int][]int)
	for _, conn := range connections {
		adj[conn[0]] = append(adj[conn[0]], conn[1])
		adj[conn[1]] = append(adj[conn[1]], conn[0])
	}

	// DFS to find components
	var dfs func(node int, component map[int]bool)
	dfs = func(node int, component map[int]bool) {
		visited[node] = true
		component[node] = true
		for _, neighbor := range adj[node] {
			if !visited[neighbor] {
				dfs(neighbor, component)
			}
		}
	}

	// Find all components
	for node := 0; node < n; node++ {
		if !visited[node] {
			component := make(map[int]bool)
			dfs(node, component)
			components = append(components, component)
		}
	}

	return components
}

func TestNetworkLayout(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			connections, nodeLocations := OptimalNetworkLayout(
				tc.nodes,
				tc.latencyMatrix,
				tc.maxConnections,
				tc.budget,
				tc.requiredConnectivity,
			)
			
			if !validateSolution(t, tc, connections, nodeLocations) {
				t.Errorf("Invalid solution for test case: %s", tc.description)
			}
		})
	}
}

func BenchmarkNetworkLayout(b *testing.B) {
	// Use the first test case for benchmarking
	tc := testCases[0]
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		OptimalNetworkLayout(
			tc.nodes,
			tc.latencyMatrix,
			tc.maxConnections,
			tc.budget,
			tc.requiredConnectivity,
		)
	}
}