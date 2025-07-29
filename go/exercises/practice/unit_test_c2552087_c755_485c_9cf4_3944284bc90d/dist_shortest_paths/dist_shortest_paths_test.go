package dist_shortest_paths

import (
	"testing"
	"time"
)

func TestGraphDistribution(t *testing.T) {
	coordinator := NewCoordinator(3)
	edges := []string{
		"1:2,10;3,5",
		"2:4,7;5,2",
		"3:5,3",
		"4:6,1",
		"5:6,4",
	}

	err := coordinator.LoadGraph(edges)
	if err != nil {
		t.Fatalf("Failed to load graph: %v", err)
	}

	if len(coordinator.workers) != 3 {
		t.Errorf("Expected 3 workers, got %d", len(coordinator.workers))
	}
}

func TestShortestPathBasic(t *testing.T) {
	coordinator := NewCoordinator(2)
	edges := []string{
		"1:2,10;3,5",
		"2:4,7",
		"3:4,3",
	}

	err := coordinator.LoadGraph(edges)
	if err != nil {
		t.Fatalf("Failed to load graph: %v", err)
	}

	weight, err := coordinator.ShortestPath(1, 4)
	if err != nil {
		t.Fatalf("ShortestPath failed: %v", err)
	}

	if weight != 8 {
		t.Errorf("Expected shortest path weight 8, got %d", weight)
	}
}

func TestShortestPathNoPath(t *testing.T) {
	coordinator := NewCoordinator(2)
	edges := []string{
		"1:2,10",
		"3:4,5",
	}

	err := coordinator.LoadGraph(edges)
	if err != nil {
		t.Fatalf("Failed to load graph: %v", err)
	}

	weight, err := coordinator.ShortestPath(1, 4)
	if err != nil {
		t.Fatalf("ShortestPath failed: %v", err)
	}

	if weight != -1 {
		t.Errorf("Expected no path (-1), got %d", weight)
	}
}

func TestConcurrentQueries(t *testing.T) {
	coordinator := NewCoordinator(4)
	edges := []string{
		"1:2,3;3,2",
		"2:4,4",
		"3:4,1",
		"4:5,5",
		"5:6,2",
	}

	err := coordinator.LoadGraph(edges)
	if err != nil {
		t.Fatalf("Failed to load graph: %v", err)
	}

	results := make(chan int, 3)
	errors := make(chan error, 3)

	go func() {
		weight, err := coordinator.ShortestPath(1, 6)
		if err != nil {
			errors <- err
			return
		}
		results <- weight
	}()

	go func() {
		weight, err := coordinator.ShortestPath(2, 5)
		if err != nil {
			errors <- err
			return
		}
		results <- weight
	}()

	go func() {
		weight, err := coordinator.ShortestPath(3, 6)
		if err != nil {
			errors <- err
			return
		}
		results <- weight
	}()

	timeout := time.After(5 * time.Second)
	var received int

	for i := 0; i < 3; i++ {
		select {
		case err := <-errors:
			t.Fatalf("Query failed: %v", err)
		case weight := <-results:
			received++
			switch weight {
			case 10, 9, 8:
				// Expected values for the three queries
			default:
				t.Errorf("Unexpected shortest path weight: %d", weight)
			}
		case <-timeout:
			t.Fatal("Timeout waiting for query results")
		}
	}

	if received != 3 {
		t.Errorf("Expected 3 results, got %d", received)
	}
}

func TestWorkerFailure(t *testing.T) {
	coordinator := NewCoordinator(3)
	edges := []string{
		"1:2,5",
		"2:3,3",
		"3:4,2",
	}

	err := coordinator.LoadGraph(edges)
	if err != nil {
		t.Fatalf("Failed to load graph: %v", err)
	}

	// Simulate worker failure
	coordinator.workers[0].Stop()

	weight, err := coordinator.ShortestPath(1, 4)
	if err != nil {
		t.Fatalf("ShortestPath failed after worker failure: %v", err)
	}

	if weight != 10 {
		t.Errorf("Expected shortest path weight 10 after worker failure, got %d", weight)
	}
}

func TestInvalidGraphData(t *testing.T) {
	coordinator := NewCoordinator(2)
	invalidEdges := []string{
		"1:2,x", // Invalid weight
	}

	err := coordinator.LoadGraph(invalidEdges)
	if err == nil {
		t.Error("Expected error for invalid graph data, got nil")
	}
}

func TestCachePerformance(t *testing.T) {
	coordinator := NewCoordinator(2)
	edges := []string{
		"1:2,5;3,3",
		"2:4,2",
		"3:4,4",
	}

	err := coordinator.LoadGraph(edges)
	if err != nil {
		t.Fatalf("Failed to load graph: %v", err)
	}

	// First query (uncached)
	start := time.Now()
	weight1, err := coordinator.ShortestPath(1, 4)
	if err != nil {
		t.Fatalf("First query failed: %v", err)
	}
	uncachedTime := time.Since(start)

	// Second query (should be cached)
	start = time.Now()
	weight2, err := coordinator.ShortestPath(1, 4)
	if err != nil {
		t.Fatalf("Second query failed: %v", err)
	}
	cachedTime := time.Since(start)

	if weight1 != weight2 {
		t.Errorf("Cached and uncached results differ: %d vs %d", weight1, weight2)
	}

	if cachedTime >= uncachedTime {
		t.Error("Cached query was not faster than uncached query")
	}
}