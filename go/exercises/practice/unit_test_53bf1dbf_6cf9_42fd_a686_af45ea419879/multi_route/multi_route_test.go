package multi_route

import (
	"math/rand"
	"testing"
	"time"
)

func TestFindShortestPath(t *testing.T) {
	testCases := []struct {
		name        string
		n           int
		k           int
		sources     []int
		destination int
		edges       [][]int
		expected    int
	}{
		{
			name:        "Simple Path",
			n:           5,
			k:           1,
			sources:     []int{0},
			destination: 4,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 2},
				{2, 3, 3},
				{3, 4, 4},
			},
			expected: 10,
		},
		{
			name:        "Multiple Sources",
			n:           6,
			k:           3,
			sources:     []int{0, 2, 4},
			destination: 5,
			edges: [][]int{
				{0, 1, 10},
				{1, 5, 20},
				{2, 3, 5},
				{3, 5, 15},
				{4, 5, 5},
			},
			expected: 5, // Direct from source 4 to destination 5
		},
		{
			name:        "No Path",
			n:           4,
			k:           2,
			sources:     []int{0, 1},
			destination: 3,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 1},
			},
			expected: -1, // No path from any source to destination
		},
		{
			name:        "Destination Is Source",
			n:           5,
			k:           3,
			sources:     []int{0, 2, 4},
			destination: 2,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 2},
				{2, 3, 3},
				{3, 4, 4},
			},
			expected: 0, // Destination is already a source
		},
		{
			name:        "Multiple Edges Between Same Nodes",
			n:           3,
			k:           1,
			sources:     []int{0},
			destination: 2,
			edges: [][]int{
				{0, 1, 5},
				{0, 1, 3}, // Better path from 0 to 1
				{1, 2, 2},
			},
			expected: 5, // 3 (from 0 to 1) + 2 (from 1 to 2)
		},
		{
			name:        "Self Loops",
			n:           4,
			k:           1,
			sources:     []int{0},
			destination: 3,
			edges: [][]int{
				{0, 0, 5}, // Self loop, should be ignored
				{0, 1, 2},
				{1, 1, 3}, // Self loop, should be ignored
				{1, 2, 4},
				{2, 3, 1},
			},
			expected: 7,
		},
		{
			name:        "Disconnected Graph",
			n:           6,
			k:           2,
			sources:     []int{0, 3},
			destination: 5,
			edges: [][]int{
				{0, 1, 1},
				{1, 2, 2}, // First component: nodes 0, 1, 2
				{3, 4, 3},
				{4, 5, 4}, // Second component: nodes 3, 4, 5
			},
			expected: 7, // Path from source 3 to destination 5
		},
		{
			name:        "Large Sparse Graph",
			n:           10,
			k:           3,
			sources:     []int{0, 3, 7},
			destination: 9,
			edges: [][]int{
				{0, 1, 5},
				{1, 2, 10},
				{2, 9, 15}, // Path from source 0: 0->1->2->9 = 30
				{3, 4, 2},
				{4, 5, 3},
				{5, 6, 4},
				{6, 9, 7}, // Path from source 3: 3->4->5->6->9 = 16
				{7, 8, 5},
				{8, 9, 6}, // Path from source 7: 7->8->9 = 11
			},
			expected: 11, // Shortest path is from source 7
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := FindShortestPath(tc.n, tc.k, tc.sources, tc.destination, tc.edges)
			if result != tc.expected {
				t.Errorf("Expected %d, got %d", tc.expected, result)
			}
		})
	}
}

// Additional test cases for edge scenarios
func TestEdgeCases(t *testing.T) {
	t.Run("Single Node", func(t *testing.T) {
		result := FindShortestPath(1, 1, []int{0}, 0, [][]int{})
		if result != 0 {
			t.Errorf("Expected 0, got %d", result)
		}
	})

	t.Run("All Nodes Are Sources", func(t *testing.T) {
		n := 5
		sources := []int{0, 1, 2, 3, 4}
		// Random destination from sources
		destination := sources[rand.Intn(len(sources))]
		result := FindShortestPath(n, len(sources), sources, destination, [][]int{
			{0, 1, 10},
			{1, 2, 20},
			{2, 3, 30},
			{3, 4, 40},
		})
		if result != 0 {
			t.Errorf("Expected 0, got %d", result)
		}
	})
}

// Performance test for large inputs
func TestLargeInput(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping large input test in short mode")
	}

	// Generate a large graph
	rand.Seed(time.Now().UnixNano())
	n := 10000
	k := 100
	sources := make([]int, k)
	for i := 0; i < k; i++ {
		sources[i] = rand.Intn(n)
	}
	destination := rand.Intn(n)

	// Check if destination is already a source
	for _, src := range sources {
		if src == destination {
			// Expected result is 0
			result := FindShortestPath(n, k, sources, destination, [][]int{})
			if result != 0 {
				t.Errorf("Expected 0 for destination in sources, got %d", result)
			}
			return
		}
	}

	// Generate edges - ensure there's at least one path to destination
	edgeCount := n * 3 // ~3 edges per node on average for a sparse graph
	edges := make([][]int, edgeCount)
	
	// First, ensure there's a path from at least one source to destination
	sourcePath := sources[rand.Intn(k)]
	currentNode := sourcePath
	pathLength := rand.Intn(10) + 1 // 1 to 10 hops
	
	for i := 0; i < pathLength; i++ {
		nextNode := rand.Intn(n)
		if i == pathLength-1 {
			nextNode = destination
		}
		edges[i] = []int{currentNode, nextNode, rand.Intn(100) + 1}
		currentNode = nextNode
	}

	// Fill in the rest of the edges randomly
	for i := pathLength; i < edgeCount; i++ {
		node1 := rand.Intn(n)
		node2 := rand.Intn(n)
		latency := rand.Intn(1000) + 1
		edges[i] = []int{node1, node2, latency}
	}

	// This test is primarily to ensure the algorithm completes in reasonable time
	start := time.Now()
	result := FindShortestPath(n, k, sources, destination, edges)
	duration := time.Since(start)
	
	t.Logf("Large input test completed in %v with result %d", duration, result)
	if result == -1 {
		t.Errorf("Expected a valid path, got -1")
	}
}

// Test for correctness with a known complex graph
func TestComplexGraph(t *testing.T) {
	n := 8
	k := 2
	sources := []int{0, 4}
	destination := 7
	edges := [][]int{
		{0, 1, 5},
		{0, 2, 8},
		{1, 3, 10},
		{2, 3, 6},
		{3, 6, 7},
		{4, 5, 4},
		{5, 6, 2},
		{6, 7, 3},
	}
	
	expected := 9 // Path: 4 -> 5 -> 6 -> 7 with latency 4+2+3=9
	result := FindShortestPath(n, k, sources, destination, edges)
	
	if result != expected {
		t.Errorf("Expected %d, got %d", expected, result)
	}
}

// Test for duplicate edges with different latencies
func TestDuplicateEdges(t *testing.T) {
	n := 5
	k := 1
	sources := []int{0}
	destination := 4
	edges := [][]int{
		{0, 1, 10},
		{0, 1, 5},  // Duplicate with better latency
		{1, 2, 8},
		{1, 2, 3},  // Duplicate with better latency
		{2, 3, 7},
		{3, 4, 4},
		{3, 4, 9},  // Duplicate with worse latency
	}
	
	expected := 19 // Path: 0 -> 1 -> 2 -> 3 -> 4 with latency 5+3+7+4=19
	result := FindShortestPath(n, k, sources, destination, edges)
	
	if result != expected {
		t.Errorf("Expected %d, got %d", expected, result)
	}
}

// Test sources or destination out of range
func TestInvalidInputs(t *testing.T) {
	testCases := []struct {
		name        string
		n           int
		k           int
		sources     []int
		destination int
		edges       [][]int
		expected    int
	}{
		{
			name:        "Source Out of Range",
			n:           5,
			k:           1,
			sources:     []int{5}, // Out of range
			destination: 4,
			edges:       [][]int{{0, 1, 1}, {1, 4, 1}},
			expected:    -1,
		},
		{
			name:        "Destination Out of Range",
			n:           5,
			k:           1,
			sources:     []int{0},
			destination: 5, // Out of range
			edges:       [][]int{{0, 1, 1}, {1, 4, 1}},
			expected:    -1,
		},
		{
			name:        "Negative Source",
			n:           5,
			k:           1,
			sources:     []int{-1}, // Invalid
			destination: 4,
			edges:       [][]int{{0, 1, 1}, {1, 4, 1}},
			expected:    -1,
		},
		{
			name:        "Negative Destination",
			n:           5,
			k:           1,
			sources:     []int{0},
			destination: -1, // Invalid
			edges:       [][]int{{0, 1, 1}, {1, 4, 1}},
			expected:    -1,
		},
		{
			name:        "Edge Node Out of Range",
			n:           5,
			k:           1,
			sources:     []int{0},
			destination: 4,
			edges:       [][]int{{0, 1, 1}, {1, 5, 1}}, // Node 5 out of range
			expected:    -1,
		},
		{
			name:        "Negative Edge Node",
			n:           5,
			k:           1,
			sources:     []int{0},
			destination: 4,
			edges:       [][]int{{0, 1, 1}, {1, -1, 1}}, // Node -1 invalid
			expected:    -1,
		},
		{
			name:        "Negative Latency",
			n:           5,
			k:           1,
			sources:     []int{0},
			destination: 4,
			edges:       [][]int{{0, 1, 1}, {1, 4, -1}}, // Negative latency
			expected:    -1,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := FindShortestPath(tc.n, tc.k, tc.sources, tc.destination, tc.edges)
			if result != tc.expected {
				t.Errorf("Expected %d, got %d", tc.expected, result)
			}
		})
	}
}