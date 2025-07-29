package dynamicrouter

import (
	"testing"
)

func TestEmptyNetwork(t *testing.T) {
	router := NewRouter(5)
	
	// Test empty network
	if path := router.GetShortestPath(0, 4); path != -1 {
		t.Errorf("Expected -1 for disconnected nodes, got %d", path)
	}
}

func TestAddAndRemoveEdge(t *testing.T) {
	router := NewRouter(5)
	
	// Add edges
	router.AddEdge(0, 1, 10)
	router.AddEdge(1, 2, 5)
	router.AddEdge(2, 3, 15)
	router.AddEdge(3, 4, 20)
	
	// Check path exists
	if path := router.GetShortestPath(0, 4); path != 50 {
		t.Errorf("Expected path length 50, got %d", path)
	}
	
	// Remove edge and check path changes
	router.RemoveEdge(2, 3)
	if path := router.GetShortestPath(0, 4); path != -1 {
		t.Errorf("Expected -1 after edge removal, got %d", path)
	}
	
	// Add alternative path
	router.AddEdge(1, 4, 30)
	
	// Check new path
	if path := router.GetShortestPath(0, 4); path != 40 {
		t.Errorf("Expected path length 40 after new edge, got %d", path)
	}
}

func TestUpdateEdge(t *testing.T) {
	router := NewRouter(5)
	
	router.AddEdge(0, 1, 10)
	router.AddEdge(1, 2, 20)
	router.AddEdge(0, 2, 50)
	
	// Initial shortest path
	if path := router.GetShortestPath(0, 2); path != 30 {
		t.Errorf("Expected path length 30, got %d", path)
	}
	
	// Update edge weight
	router.AddEdge(0, 2, 25)
	
	// Check updated path
	if path := router.GetShortestPath(0, 2); path != 25 {
		t.Errorf("Expected path length 25 after edge update, got %d", path)
	}
}

func TestMultipleRoutes(t *testing.T) {
	router := NewRouter(6)
	
	router.AddEdge(0, 1, 10)
	router.AddEdge(1, 2, 20)
	router.AddEdge(2, 5, 10)
	router.AddEdge(0, 3, 15)
	router.AddEdge(3, 4, 10)
	router.AddEdge(4, 5, 15)
	
	// Check shortest path
	if path := router.GetShortestPath(0, 5); path != 40 {
		t.Errorf("Expected path length 40, got %d", path)
	}
	
	// Remove edge in shortest path
	router.RemoveEdge(2, 5)
	
	// Check new shortest path
	if path := router.GetShortestPath(0, 5); path != 40 {
		t.Errorf("Expected path length 40 after edge removal, got %d", path)
	}
	
	// Remove another edge
	router.RemoveEdge(4, 5)
	
	// Check disconnected
	if path := router.GetShortestPath(0, 5); path != -1 {
		t.Errorf("Expected -1 after all paths removed, got %d", path)
	}
}

func TestLargeNetwork(t *testing.T) {
	n := 1000
	router := NewRouter(n)
	
	// Create a line graph
	for i := 0; i < n-1; i++ {
		router.AddEdge(i, i+1, 1)
	}
	
	// Test path in large graph
	if path := router.GetShortestPath(0, n-1); path != n-1 {
		t.Errorf("Expected path length %d, got %d", n-1, path)
	}
	
	// Remove middle edge
	middle := n / 2
	router.RemoveEdge(middle, middle+1)
	
	// Test disconnected path
	if path := router.GetShortestPath(0, n-1); path != -1 {
		t.Errorf("Expected -1 after middle edge removal, got %d", path)
	}
	
	// Add alternative path
	router.AddEdge(middle, middle+1, 5)
	
	// Test path with higher weight edge
	if path := router.GetShortestPath(0, n-1); path != n-1+4 {
		t.Errorf("Expected path length %d, got %d", n-1+4, path)
	}
}

func TestMultithreadSafety(t *testing.T) {
	// This doesn't explicitly test thread safety but is here to remind
	// that implementations should consider concurrency
	router := NewRouter(10)
	
	router.AddEdge(0, 1, 5)
	router.AddEdge(1, 2, 5)
	router.AddEdge(2, 3, 5)
	
	if path := router.GetShortestPath(0, 3); path != 15 {
		t.Errorf("Expected path length 15, got %d", path)
	}
}

func TestSelfLoop(t *testing.T) {
	router := NewRouter(5)
	
	// Add a self loop
	router.AddEdge(1, 1, 10)
	router.AddEdge(1, 2, 5)
	
	// Self loops shouldn't affect shortest path
	if path := router.GetShortestPath(1, 2); path != 5 {
		t.Errorf("Expected path length 5, got %d", path)
	}
	
	// Removing self loop
	router.RemoveEdge(1, 1)
	
	// Path should remain the same
	if path := router.GetShortestPath(1, 2); path != 5 {
		t.Errorf("Expected path length 5 after self loop removal, got %d", path)
	}
}

func TestParallelEdges(t *testing.T) {
	router := NewRouter(5)
	
	// Add edge
	router.AddEdge(1, 2, 10)
	
	// Add same edge with different weight (update)
	router.AddEdge(1, 2, 5)
	
	// Check updated weight is used
	if path := router.GetShortestPath(1, 2); path != 5 {
		t.Errorf("Expected path length 5 after edge update, got %d", path)
	}
}

func TestSameSourceAndDestination(t *testing.T) {
	router := NewRouter(5)
	
	// Distance to self should be 0
	if path := router.GetShortestPath(3, 3); path != 0 {
		t.Errorf("Expected path length 0 for same source and destination, got %d", path)
	}
}

func BenchmarkAddEdge(b *testing.B) {
	n := 1000
	router := NewRouter(n)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		src := i % n
		dst := (i + 1) % n
		router.AddEdge(src, dst, i%100+1)
	}
}

func BenchmarkRemoveEdge(b *testing.B) {
	n := 1000
	router := NewRouter(n)
	
	// Add edges first
	for i := 0; i < n; i++ {
		router.AddEdge(i, (i+1)%n, i%100+1)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		src := i % n
		dst := (i + 1) % n
		router.RemoveEdge(src, dst)
	}
}

func BenchmarkGetShortestPath(b *testing.B) {
	n := 1000
	router := NewRouter(n)
	
	// Create a connected graph
	for i := 0; i < n; i++ {
		router.AddEdge(i, (i+1)%n, 1)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		src := i % n
		dst := (i + n/2) % n
		router.GetShortestPath(src, dst)
	}
}

func BenchmarkDynamicRouting(b *testing.B) {
	n := 1000
	router := NewRouter(n)
	
	// Setup initial graph
	for i := 0; i < n; i++ {
		router.AddEdge(i, (i+1)%n, 1)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		op := i % 3
		src := i % n
		dst := (i + n/2) % n
		
		switch op {
		case 0:
			router.AddEdge(src, dst, i%10+1)
		case 1:
			router.RemoveEdge(src, dst)
		case 2:
			router.GetShortestPath(src, dst)
		}
	}
}