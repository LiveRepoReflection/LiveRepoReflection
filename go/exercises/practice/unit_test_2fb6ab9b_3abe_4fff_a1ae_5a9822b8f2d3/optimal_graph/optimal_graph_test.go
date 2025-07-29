package optimalgraph

import (
	"reflect"
	"testing"
)

func TestOptimalGraph(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			actual := OptimalGraph(tc.n, tc.capacities, tc.generations, tc.dependencies)
			
			// Check if result is a valid DAG
			if !isValidDAG(actual, tc.n) {
				t.Fatalf("Result is not a valid DAG")
			}
			
			// Check capacity constraints
			if !respectsCapacityConstraints(actual, tc.n, tc.capacities, tc.generations) {
				t.Fatalf("Result does not respect capacity constraints")
			}
			
			// Verify if the expected solution is also valid
			if isValidSolution(tc.expected, tc.n, tc.capacities, tc.generations, tc.dependencies) {
				// If the expected is valid, check if our actual solution has equal or lower max latency
				expectedMaxLatency := calculateMaxLatency(tc.expected, tc.n, tc.dependencies)
				actualMaxLatency := calculateMaxLatency(actual, tc.n, tc.dependencies)
				
				if actualMaxLatency > expectedMaxLatency {
					t.Fatalf("Expected max latency %d, but got %d", expectedMaxLatency, actualMaxLatency)
				}
			} else if !reflect.DeepEqual(actual, tc.expected) && !isAllFalse(tc.expected) {
				// Only compare directly if the expected isn't all false (which means no solution)
				t.Fatalf("Expected %v, but got %v", tc.expected, actual)
			}
		})
	}
}

// isValidDAG checks if the graph is a valid Directed Acyclic Graph
func isValidDAG(graph [][]bool, n int) bool {
	// Check for cycles using DFS
	visited := make([]bool, n)
	recursionStack := make([]bool, n)
	
	for i := 0; i < n; i++ {
		if !visited[i] {
			if hasCycleDFS(graph, i, visited, recursionStack) {
				return false
			}
		}
	}
	
	return true
}

// hasCycleDFS uses depth-first search to detect cycles
func hasCycleDFS(graph [][]bool, node int, visited, recursionStack []bool) bool {
	visited[node] = true
	recursionStack[node] = true
	
	for neighbor := 0; neighbor < len(graph[node]); neighbor++ {
		if graph[node][neighbor] {
			if !visited[neighbor] {
				if hasCycleDFS(graph, neighbor, visited, recursionStack) {
					return true
				}
			} else if recursionStack[neighbor] {
				return true
			}
		}
	}
	
	recursionStack[node] = false
	return false
}

// respectsCapacityConstraints checks if the solution respects all capacity constraints
func respectsCapacityConstraints(graph [][]bool, n int, capacities, generations []int) bool {
	incomingRequests := make([]int, n)
	
	// Calculate incoming requests for each service
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			if graph[i][j] {
				incomingRequests[j] += generations[i]
			}
		}
	}
	
	// Check capacity constraints
	for i := 0; i < n; i++ {
		if incomingRequests[i] > capacities[i] {
			return false
		}
	}
	
	return true
}

// isValidSolution checks if a given solution is valid
func isValidSolution(graph [][]bool, n int, capacities, generations []int, dependencies [][]int) bool {
	// Check if it's a DAG
	if !isValidDAG(graph, n) {
		return false
	}
	
	// Check capacity constraints
	if !respectsCapacityConstraints(graph, n, capacities, generations) {
		return false
	}
	
	// Check if dependencies are respected
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			if graph[i][j] {
				// If there's an edge from i to j, j must be in the dependencies of i
				found := false
				for _, dep := range dependencies[i] {
					if dep == j {
						found = true
						break
					}
				}
				if !found {
					return false
				}
			}
		}
	}
	
	return true
}

// calculateMaxLatency calculates the maximum latency in the communication graph
func calculateMaxLatency(graph [][]bool, n int, dependencies [][]int) int {
	// Use dynamic programming to calculate the longest path in the DAG
	longestPath := make([]int, n)
	
	// Topological sort
	visited := make([]bool, n)
	stack := []int{}
	
	var topoSort func(int)
	topoSort = func(node int) {
		visited[node] = true
		
		for neighbor := 0; neighbor < n; neighbor++ {
			if graph[node][neighbor] && !visited[neighbor] {
				topoSort(neighbor)
			}
		}
		
		stack = append(stack, node)
	}
	
	for i := 0; i < n; i++ {
		if !visited[i] {
			topoSort(i)
		}
	}
	
	// Calculate longest paths
	maxLatency := 0
	
	for i := len(stack) - 1; i >= 0; i-- {
		node := stack[i]
		
		for neighbor := 0; neighbor < n; neighbor++ {
			if graph[node][neighbor] {
				longestPath[neighbor] = max(longestPath[neighbor], longestPath[node]+1)
				maxLatency = max(maxLatency, longestPath[neighbor])
			}
		}
	}
	
	return maxLatency
}

// isAllFalse checks if the graph is all false values (no solution)
func isAllFalse(graph [][]bool) bool {
	for i := 0; i < len(graph); i++ {
		for j := 0; j < len(graph[i]); j++ {
			if graph[i][j] {
				return false
			}
		}
	}
	return true
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func BenchmarkOptimalGraph(b *testing.B) {
	// Use one of the test cases for benchmarking
	tc := testCases[5] // Using the complex dependencies test case
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalGraph(tc.n, tc.capacities, tc.generations, tc.dependencies)
	}
}