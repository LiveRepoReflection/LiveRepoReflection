package dynamicgraph

import (
	"math"
	"math/rand"
	"testing"
	"time"
)

func TestDynamicGraph_Basic(t *testing.T) {
	g := NewDynamicGraph()
	
	// Add nodes
	g.AddNode(1)
	g.AddNode(2)
	g.AddNode(3)
	
	// Add edges
	g.AddEdge(1, 2, 5)
	g.AddEdge(2, 3, 3)
	g.AddEdge(1, 3, 10)
	
	// Test shortest path
	if dist := g.ShortestPath(1, 3); dist != 8 {
		t.Errorf("Expected shortest path from 1 to 3 to be 8, got %d", dist)
	}
	
	// Remove an edge and test again
	g.RemoveEdge(1, 2)
	if dist := g.ShortestPath(1, 3); dist != 10 {
		t.Errorf("After removing edge (1,2), expected shortest path from 1 to 3 to be 10, got %d", dist)
	}
	
	// Add the edge back with a different weight
	g.AddEdge(1, 2, 2)
	if dist := g.ShortestPath(1, 3); dist != 5 {
		t.Errorf("After adding edge (1,2) with weight 2, expected shortest path from 1 to 3 to be 5, got %d", dist)
	}
	
	// Remove a node and test
	g.RemoveNode(2)
	if dist := g.ShortestPath(1, 3); dist != 10 {
		t.Errorf("After removing node 2, expected shortest path from 1 to 3 to be 10, got %d", dist)
	}
	
	// Test non-existent path
	g.RemoveEdge(1, 3)
	if dist := g.ShortestPath(1, 3); dist != math.MaxInt {
		t.Errorf("Expected no path from 1 to 3, got %d", dist)
	}
}

func TestDynamicGraph_NegativeWeights(t *testing.T) {
	g := NewDynamicGraph()
	
	// Add nodes
	g.AddNode(1)
	g.AddNode(2)
	g.AddNode(3)
	g.AddNode(4)
	
	// Add edges with negative weights
	g.AddEdge(1, 2, 4)
	g.AddEdge(2, 3, -2)
	g.AddEdge(3, 4, 3)
	g.AddEdge(1, 4, 10)
	
	// Test shortest path with negative edge
	if dist := g.ShortestPath(1, 4); dist != 5 {
		t.Errorf("Expected shortest path from 1 to 4 to be 5, got %d", dist)
	}
}

func TestDynamicGraph_NonExistentNodes(t *testing.T) {
	g := NewDynamicGraph()
	
	// Test operations with non-existent nodes
	if dist := g.ShortestPath(1, 2); dist != math.MaxInt {
		t.Errorf("Expected no path between non-existent nodes, got %d", dist)
	}
	
	// Add a node
	g.AddNode(1)
	
	// Test again with one node existing and one not
	if dist := g.ShortestPath(1, 2); dist != math.MaxInt {
		t.Errorf("Expected no path to non-existent node, got %d", dist)
	}
	
	// Test adding an edge to a non-existent node (should be ignored)
	g.AddEdge(1, 2, 5)
	if dist := g.ShortestPath(1, 2); dist != math.MaxInt {
		t.Errorf("Expected no path to non-existent node after attempted edge add, got %d", dist)
	}
}

func TestDynamicGraph_DuplicateNodeAdd(t *testing.T) {
	g := NewDynamicGraph()
	
	// Add a node twice
	g.AddNode(1)
	g.AddNode(1) // Should be ignored
	
	// Add another node and an edge
	g.AddNode(2)
	g.AddEdge(1, 2, 5)
	
	// Test shortest path
	if dist := g.ShortestPath(1, 2); dist != 5 {
		t.Errorf("Expected shortest path to be 5 after duplicate node add, got %d", dist)
	}
}

func TestDynamicGraph_EdgeUpdate(t *testing.T) {
	g := NewDynamicGraph()
	
	// Add nodes
	g.AddNode(1)
	g.AddNode(2)
	g.AddNode(3)
	
	// Add edges
	g.AddEdge(1, 2, 5)
	g.AddEdge(2, 3, 3)
	
	// Test initial shortest path
	if dist := g.ShortestPath(1, 3); dist != 8 {
		t.Errorf("Expected initial shortest path from 1 to 3 to be 8, got %d", dist)
	}
	
	// Update an edge
	g.AddEdge(1, 2, 2) // Update weight from 5 to 2
	
	// Test updated shortest path
	if dist := g.ShortestPath(1, 3); dist != 5 {
		t.Errorf("Expected updated shortest path from 1 to 3 to be 5, got %d", dist)
	}
}

func TestDynamicGraph_LargeRandomGraph(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping large random graph test in short mode")
	}
	
	rand.Seed(time.Now().UnixNano())
	g := NewDynamicGraph()
	
	const (
		nodeCount     = 100
		edgeCount     = 500
		operationCount = 1000
	)
	
	// Add nodes
	for i := 1; i <= nodeCount; i++ {
		g.AddNode(i)
	}
	
	// Add random edges
	for i := 0; i < edgeCount; i++ {
		src := rand.Intn(nodeCount) + 1
		dst := rand.Intn(nodeCount) + 1
		weight := rand.Intn(2000) - 1000 // -1000 to 999
		g.AddEdge(src, dst, weight)
	}
	
	// Perform random operations
	for i := 0; i < operationCount; i++ {
		op := rand.Intn(5)
		switch op {
		case 0: // AddNode
			nodeID := rand.Intn(nodeCount) + 1
			g.AddNode(nodeID)
		case 1: // RemoveNode
			nodeID := rand.Intn(nodeCount) + 1
			g.RemoveNode(nodeID)
		case 2: // AddEdge
			src := rand.Intn(nodeCount) + 1
			dst := rand.Intn(nodeCount) + 1
			weight := rand.Intn(2000) - 1000
			g.AddEdge(src, dst, weight)
		case 3: // RemoveEdge
			src := rand.Intn(nodeCount) + 1
			dst := rand.Intn(nodeCount) + 1
			g.RemoveEdge(src, dst)
		case 4: // ShortestPath
			src := rand.Intn(nodeCount) + 1
			dst := rand.Intn(nodeCount) + 1
			g.ShortestPath(src, dst) // Just make sure it doesn't crash
		}
	}
}

func TestDynamicGraph_PerformanceShortestPath(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping performance test in short mode")
	}
	
	g := NewDynamicGraph()
	
	// Create a larger graph for performance testing
	const nodeCount = 1000
	
	// Add nodes
	for i := 1; i <= nodeCount; i++ {
		g.AddNode(i)
	}
	
	// Add edges in a grid-like pattern (with some random edges)
	for i := 1; i <= nodeCount; i++ {
		// Connect to next 10 nodes with random weights
		for j := 1; j <= 10; j++ {
			if i+j <= nodeCount {
				weight := rand.Intn(100) + 1
				g.AddEdge(i, i+j, weight)
			}
		}
	}
	
	// Time shortest path queries
	start := time.Now()
	const queries = 100
	for i := 0; i < queries; i++ {
		src := rand.Intn(nodeCount) + 1
		dst := rand.Intn(nodeCount) + 1
		g.ShortestPath(src, dst)
	}
	duration := time.Since(start)
	
	// Report average time per query
	t.Logf("Average time per shortest path query: %v", duration/queries)
}

func BenchmarkDynamicGraph_ShortestPath(b *testing.B) {
	g := NewDynamicGraph()
	
	// Create a medium-sized graph
	const nodeCount = 500
	
	// Add nodes
	for i := 1; i <= nodeCount; i++ {
		g.AddNode(i)
	}
	
	// Add edges in a grid-like pattern
	for i := 1; i <= nodeCount; i++ {
		// Connect to next 5 nodes
		for j := 1; j <= 5; j++ {
			if i+j <= nodeCount {
				weight := rand.Intn(100) + 1
				g.AddEdge(i, i+j, weight)
			}
		}
	}
	
	// Reset timer before the actual benchmark
	b.ResetTimer()
	
	// Run the benchmark
	for i := 0; i < b.N; i++ {
		src := rand.Intn(nodeCount) + 1
		dst := rand.Intn(nodeCount) + 1
		g.ShortestPath(src, dst)
	}
}

func BenchmarkDynamicGraph_AddRemoveNode(b *testing.B) {
	g := NewDynamicGraph()
	
	// Reset timer before the actual benchmark
	b.ResetTimer()
	
	// Run the benchmark
	for i := 0; i < b.N; i++ {
		nodeID := i % 10000 // Keep IDs within a reasonable range
		g.AddNode(nodeID)
		g.RemoveNode(nodeID)
	}
}

func BenchmarkDynamicGraph_AddRemoveEdge(b *testing.B) {
	g := NewDynamicGraph()
	
	// Add some nodes first
	for i := 1; i <= 1000; i++ {
		g.AddNode(i)
	}
	
	// Reset timer before the actual benchmark
	b.ResetTimer()
	
	// Run the benchmark
	for i := 0; i < b.N; i++ {
		src := (i % 1000) + 1
		dst := ((i + 1) % 1000) + 1
		weight := i % 2000 - 1000
		g.AddEdge(src, dst, weight)
		g.RemoveEdge(src, dst)
	}
}

func TestDynamicGraph_MixedOperations(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping mixed operations test in short mode")
	}
	
	g := NewDynamicGraph()
	
	// Add initial nodes and edges
	for i := 1; i <= 20; i++ {
		g.AddNode(i)
	}
	
	// Add some initial edges
	g.AddEdge(1, 2, 5)
	g.AddEdge(2, 3, 3)
	g.AddEdge(3, 4, 2)
	g.AddEdge(4, 5, 1)
	g.AddEdge(1, 5, 20)
	
	// Test a known path
	if dist := g.ShortestPath(1, 5); dist != 11 {
		t.Errorf("Expected shortest path from 1 to 5 to be 11, got %d", dist)
	}
	
	// Modify the graph
	g.RemoveNode(3)
	
	// Test again
	if dist := g.ShortestPath(1, 5); dist != 20 {
		t.Errorf("After removing node 3, expected shortest path from 1 to 5 to be 20, got %d", dist)
	}
	
	// Add more edges
	g.AddEdge(1, 6, 2)
	g.AddEdge(6, 7, 3)
	g.AddEdge(7, 5, 1)
	
	// Test again
	if dist := g.ShortestPath(1, 5); dist != 6 {
		t.Errorf("After adding new path, expected shortest path from 1 to 5 to be 6, got %d", dist)
	}
	
	// Add a negative weight edge
	g.AddEdge(6, 5, -1)
	
	// Test again
	if dist := g.ShortestPath(1, 5); dist != 1 {
		t.Errorf("After adding negative edge, expected shortest path from 1 to 5 to be 1, got %d", dist)
	}
}