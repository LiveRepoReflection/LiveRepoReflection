package optimal_routing

import (
	"math"
	"testing"
	"time"
)

func TestFindOptimalRoute(t *testing.T) {
	tests := []struct {
		name      string
		startNode int
		endNode   int
		adj       [][]int
		costs     [][]int
		maxTime   int
		want      int
	}{
		{
			name:      "Example 1: Path 0->1->3",
			startNode: 0,
			endNode:   3,
			adj: [][]int{
				{1, 2},
				{0, 3},
				{0, 4},
				{1},
				{2},
			},
			costs: [][]int{
				{0, 2, 3, 1000, 1000},
				{2, 0, 1000, 4, 1000},
				{3, 1000, 0, 1000, 5},
				{1000, 4, 1000, 0, 1000},
				{1000, 1000, 5, 1000, 0},
			},
			maxTime: 100,
			want:    6,
		},
		{
			name:      "Example 2: Path 0->2->4",
			startNode: 0,
			endNode:   4,
			adj: [][]int{
				{1, 2},
				{0, 3},
				{0, 4},
				{1},
				{2},
			},
			costs: [][]int{
				{0, 2, 3, 1000, 1000},
				{2, 0, 1000, 4, 1000},
				{3, 1000, 0, 1000, 5},
				{1000, 4, 1000, 0, 1000},
				{1000, 1000, 5, 1000, 0},
			},
			maxTime: 100,
			want:    8,
		},
		{
			name:      "Same Start and End Node",
			startNode: 1,
			endNode:   1,
			adj: [][]int{
				{1},
				{0, 2},
				{1},
			},
			costs: [][]int{
				{0, 5, 1000},
				{5, 0, 3},
				{1000, 3, 0},
			},
			maxTime: 100,
			want:    0,
		},
		{
			name:      "No Path Exists",
			startNode: 0,
			endNode:   3,
			adj: [][]int{
				{1},
				{0},
				{3},
				{2},
			},
			costs: [][]int{
				{0, 1, 1000, 1000},
				{1, 0, 1000, 1000},
				{1000, 1000, 0, 1},
				{1000, 1000, 1, 0},
			},
			maxTime: 100,
			want:    -1,
		},
		{
			name:      "Larger Network",
			startNode: 0,
			endNode:   5,
			adj: [][]int{
				{1, 2},
				{0, 3, 4},
				{0, 4},
				{1, 5},
				{1, 2, 5},
				{3, 4},
			},
			costs: [][]int{
				{0, 1, 5, 1000, 1000, 1000},
				{1, 0, 1000, 2, 1, 1000},
				{5, 1000, 0, 1000, 3, 1000},
				{1000, 2, 1000, 0, 1000, 1},
				{1000, 1, 3, 1000, 0, 4},
				{1000, 1000, 1000, 1, 4, 0},
			},
			maxTime: 100,
			want:    4, // Path: 0->1->3->5
		},
		{
			name:      "Complex Network With Multiple Paths",
			startNode: 0,
			endNode:   6,
			adj: [][]int{
				{1, 2, 3},
				{0, 2, 4},
				{0, 1, 3, 5},
				{0, 2, 5},
				{1, 5, 6},
				{2, 3, 4, 6},
				{4, 5},
			},
			costs: [][]int{
				{0, 7, 9, 8, 1000, 1000, 1000},
				{7, 0, 10, 1000, 15, 1000, 1000},
				{9, 10, 0, 11, 1000, 2, 1000},
				{8, 1000, 11, 0, 1000, 6, 1000},
				{1000, 15, 1000, 1000, 0, 12, 7},
				{1000, 1000, 2, 6, 12, 0, 5},
				{1000, 1000, 1000, 1000, 7, 5, 0},
			},
			maxTime: 100,
			want:    16, // Best path: 0->2->5->6
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := FindOptimalRoute(tt.startNode, tt.endNode, tt.adj, tt.costs, tt.maxTime); got != tt.want {
				t.Errorf("FindOptimalRoute() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestFindOptimalRouteTimeConstraint(t *testing.T) {
	// Create a large network to test the time constraint
	n := 1000
	adj := make([][]int, n)
	costs := make([][]int, n)
	
	// Initialize with a simple grid-like structure
	for i := 0; i < n; i++ {
		costs[i] = make([]int, n)
		for j := 0; j < n; j++ {
			if i != j {
				costs[i][j] = math.MaxInt32 / 2 // Use a large value that won't overflow when added
			}
		}
		
		// Connect to neighbors (up to 4 connections in a grid-like structure)
		if i > 0 {
			adj[i] = append(adj[i], i-1)
			costs[i][i-1] = 1
		}
		if i < n-1 {
			adj[i] = append(adj[i], i+1)
			costs[i][i+1] = 1
		}
		if i >= 30 { // Add some long-range connections
			adj[i] = append(adj[i], i-30)
			costs[i][i-30] = 5
		}
		if i+30 < n {
			adj[i] = append(adj[i], i+30)
			costs[i][i+30] = 5
		}
	}
	
	// Add some random long-range connections for complexity
	for i := 0; i < n/10; i++ {
		from := (i * 10) % n
		to := (i * 10 + 100) % n
		adj[from] = append(adj[from], to)
		adj[to] = append(adj[to], from)
		costs[from][to] = 10
		costs[to][from] = 10
	}
	
	testCases := []struct {
		maxTime   int
		startNode int
		endNode   int
	}{
		{maxTime: 100, startNode: 0, endNode: n - 1},
		{maxTime: 200, startNode: n/2, endNode: n - 10},
		{maxTime: 50, startNode: 10, endNode: 500},
	}
	
	for _, tc := range testCases {
		t.Run("Time Constraint Test", func(t *testing.T) {
			start := time.Now()
			result := FindOptimalRoute(tc.startNode, tc.endNode, adj, costs, tc.maxTime)
			elapsed := time.Since(start)
			
			// Check if the function returned within the time limit
			if elapsed > time.Duration(tc.maxTime)*time.Millisecond {
				t.Errorf("FindOptimalRoute took %v, exceeding the time limit of %dms", elapsed, tc.maxTime)
			}
			
			// Verify that the result is reasonable (not checking exact value since we're testing time performance)
			if result == -1 {
				t.Logf("No path found within time constraint")
			} else if result <= 0 && tc.startNode != tc.endNode {
				t.Errorf("Expected positive cost for path from %d to %d, got %d", tc.startNode, tc.endNode, result)
			}
		})
	}
}

func TestDynamicNetworkChanges(t *testing.T) {
	// Initial network
	adj := [][]int{
		{1, 2},
		{0, 3},
		{0, 4},
		{1},
		{2},
	}
	costs := [][]int{
		{0, 2, 3, 1000, 1000},
		{2, 0, 1000, 4, 1000},
		{3, 1000, 0, 1000, 5},
		{1000, 4, 1000, 0, 1000},
		{1000, 1000, 5, 1000, 0},
	}
	
	// First test - original network
	if got := FindOptimalRoute(0, 3, adj, costs, 100); got != 6 {
		t.Errorf("Initial network: FindOptimalRoute(0, 3) = %v, want 6", got)
	}
	
	// Modify the network - add a direct connection from 0 to 3
	adj[0] = append(adj[0], 3)
	adj[3] = append(adj[3], 0)
	costs[0][3] = 5
	costs[3][0] = 5
	
	// Test after modification
	if got := FindOptimalRoute(0, 3, adj, costs, 100); got != 5 {
		t.Errorf("After adding direct connection: FindOptimalRoute(0, 3) = %v, want 5", got)
	}
	
	// Further modify - change costs
	costs[0][1] = 1  // Make path 0->1->3 (total cost 5) same as direct path
	
	// Test after cost change
	if got := FindOptimalRoute(0, 3, adj, costs, 100); got != 5 {
		t.Errorf("After changing costs: FindOptimalRoute(0, 3) = %v, want 5", got)
	}
	
	// Remove connections to make the target unreachable
	adj[0] = []int{2}
	adj[3] = []int{}
	costs[0][1] = 1000
	costs[0][3] = 1000
	costs[1][0] = 1000
	costs[3][0] = 1000
	costs[1][3] = 1000
	costs[3][1] = 1000
	
	// Test for unreachable target
	if got := FindOptimalRoute(0, 3, adj, costs, 100); got != -1 {
		t.Errorf("After making unreachable: FindOptimalRoute(0, 3) = %v, want -1", got)
	}
}

func BenchmarkFindOptimalRoute(b *testing.B) {
	// Create a medium-sized network for benchmarking
	n := 100
	adj := make([][]int, n)
	costs := make([][]int, n)
	
	// Initialize network
	for i := 0; i < n; i++ {
		costs[i] = make([]int, n)
		for j := 0; j < n; j++ {
			if i != j {
				costs[i][j] = math.MaxInt32 / 2
			}
		}
		
		// Connect to neighbors
		if i > 0 {
			adj[i] = append(adj[i], i-1)
			costs[i][i-1] = i % 5 + 1
		}
		if i < n-1 {
			adj[i] = append(adj[i], i+1)
			costs[i][i+1] = i % 5 + 1
		}
		// Add some cross connections
		if i % 10 == 0 && i+10 < n {
			adj[i] = append(adj[i], i+10)
			adj[i+10] = append(adj[i+10], i)
			costs[i][i+10] = 7
			costs[i+10][i] = 7
		}
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		start := i % n
		end := (start + n/2) % n
		FindOptimalRoute(start, end, adj, costs, 200)
	}
}