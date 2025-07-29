package dist_shortest_path

import (
	"reflect"
	"testing"
)

// TestDirectConnection tests a simple graph with a direct edge between source and destination.
func TestDirectConnection(t *testing.T) {
	// Graph: A <-> B with weight 1.0.
	graphData := map[string]map[string]float64{
		"A": {"B": 1.0},
		"B": {"A": 1.0},
	}
	expectedPath := []string{"A", "B"}
	expectedCost := 1.0

	path, cost, err := FindShortestPath("A", "B", graphData)
	if err != nil {
		t.Fatalf("Unexpected error for direct connection: %v", err)
	}
	if !reflect.DeepEqual(path, expectedPath) {
		t.Fatalf("Expected path %v, got %v", expectedPath, path)
	}
	if cost != expectedCost {
		t.Fatalf("Expected cost %v, got %v", expectedCost, cost)
	}
}

// TestMultiplePaths tests a graph that has several possible paths between the source and destination.
// It checks that the function returns the optimal (lowest cost) path.
func TestMultiplePaths(t *testing.T) {
	// Graph:
	// A -1-> B, A -4-> C, B -2-> C, C -1-> D, B -5-> D.
	graphData := map[string]map[string]float64{
		"A": {"B": 1.0, "C": 4.0},
		"B": {"A": 1.0, "C": 2.0, "D": 5.0},
		"C": {"A": 4.0, "B": 2.0, "D": 1.0},
		"D": {"B": 5.0, "C": 1.0},
	}
	expectedPath := []string{"A", "B", "C", "D"}
	expectedCost := 4.0

	path, cost, err := FindShortestPath("A", "D", graphData)
	if err != nil {
		t.Fatalf("Unexpected error for multiple paths: %v", err)
	}
	if !reflect.DeepEqual(path, expectedPath) {
		t.Fatalf("Expected path %v, got %v", expectedPath, path)
	}
	if cost != expectedCost {
		t.Fatalf("Expected cost %v, got %v", expectedCost, cost)
	}

	// Also test the reverse direction: from D to A.
	expectedPathReverse := []string{"D", "C", "B", "A"}
	path, cost, err = FindShortestPath("D", "A", graphData)
	if err != nil {
		t.Fatalf("Unexpected error for reverse direction: %v", err)
	}
	if !reflect.DeepEqual(path, expectedPathReverse) {
		t.Fatalf("Expected reverse path %v, got %v", expectedPathReverse, path)
	}
	if cost != expectedCost {
		t.Fatalf("Expected cost %v, got %v", expectedCost, cost)
	}
}

// TestNoPath tests the scenario when there is no available path between the source and destination.
func TestNoPath(t *testing.T) {
	// Graph with disconnected nodes.
	graphData := map[string]map[string]float64{
		"A": {"B": 1.0},
		"B": {"A": 1.0},
		"C": {},
	}
	// No path exists between A and C.
	path, cost, err := FindShortestPath("A", "C", graphData)
	if err == nil {
		t.Fatalf("Expected error for no path, got nil")
	}
	if len(path) != 0 {
		t.Fatalf("Expected empty path for no connectivity, got %v", path)
	}
	if cost != -1.0 {
		t.Fatalf("Expected cost -1.0 for no connectivity, got %v", cost)
	}
}

// TestSourceEqualsDestination tests the edge case when the source and destination are the same.
func TestSourceEqualsDestination(t *testing.T) {
	// When source equals destination, the function should return the source only with 0 cost.
	graphData := map[string]map[string]float64{
		"A": {"B": 1.0},
		"B": {"A": 1.0},
	}
	expectedPath := []string{"A"}
	expectedCost := 0.0

	path, cost, err := FindShortestPath("A", "A", graphData)
	if err != nil {
		t.Fatalf("Unexpected error when source equals destination: %v", err)
	}
	if !reflect.DeepEqual(path, expectedPath) {
		t.Fatalf("Expected path %v, got %v", expectedPath, path)
	}
	if cost != expectedCost {
		t.Fatalf("Expected cost %v, got %v", expectedCost, cost)
	}
}

// TestLargeGraph constructs a larger ring topology graph to assess scalability and performance on a non-trivial topology.
func TestLargeGraph(t *testing.T) {
	// Construct a ring topology with 10 nodes.
	graphData := make(map[string]map[string]float64)
	nodes := []string{"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
	n := len(nodes)
	for i := 0; i < n; i++ {
		graphData[nodes[i]] = make(map[string]float64)
		// Connect each node to the next node, and the last node wraps around to the first.
		next := nodes[(i+1)%n]
		graphData[nodes[i]][next] = 1.0
		// Ensure bidirectional connections.
		if _, ok := graphData[next]; !ok {
			graphData[next] = make(map[string]float64)
		}
		graphData[next][nodes[i]] = 1.0
	}
	// The shortest path from A to F is along the ring.
	expectedPath := []string{"A", "B", "C", "D", "E", "F"}
	expectedCost := 5.0

	path, cost, err := FindShortestPath("A", "F", graphData)
	if err != nil {
		t.Fatalf("Unexpected error for large graph: %v", err)
	}
	if !reflect.DeepEqual(path, expectedPath) {
		t.Fatalf("Expected path %v, got %v", expectedPath, path)
	}
	if cost != expectedCost {
		t.Fatalf("Expected cost %v, got %v", expectedCost, cost)
	}
}