package distributed_path

import (
	"testing"
	"time"
)

func TestShortestPathInStaticNetwork(t *testing.T) {
	// Initialize a simple static network
	nodes := map[string]map[string]int{
		"A": {"B": 1, "C": 4},
		"B": {"A": 1, "C": 2, "D": 5},
		"C": {"A": 4, "B": 2, "D": 1},
		"D": {"B": 5, "C": 1},
	}

	network := NewNetwork(nodes)
	
	path, cost, err := network.FindShortestPath("A", "D")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	expectedPath := []string{"A", "B", "C", "D"}
	expectedCost := 4

	if cost != expectedCost {
		t.Errorf("Expected cost %d, got %d", expectedCost, cost)
	}

	if !equalPaths(path, expectedPath) {
		t.Errorf("Expected path %v, got %v", expectedPath, path)
	}
}

func TestShortestPathWithNodeFailure(t *testing.T) {
	nodes := map[string]map[string]int{
		"A": {"B": 1, "C": 4},
		"B": {"A": 1, "C": 2, "D": 5},
		"C": {"A": 4, "B": 2, "D": 1},
		"D": {"B": 5, "C": 1},
	}

	network := NewNetwork(nodes)
	
	// Simulate node failure
	network.MarkNodeOffline("C")

	path, cost, err := network.FindShortestPath("A", "D")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	expectedPath := []string{"A", "B", "D"}
	expectedCost := 6

	if cost != expectedCost {
		t.Errorf("Expected cost %d, got %d", expectedCost, cost)
	}

	if !equalPaths(path, expectedPath) {
		t.Errorf("Expected path %v, got %v", expectedPath, path)
	}
}

func TestShortestPathWithDynamicUpdates(t *testing.T) {
	nodes := map[string]map[string]int{
		"A": {"B": 1, "C": 4},
		"B": {"A": 1, "C": 2, "D": 5},
		"C": {"A": 4, "B": 2, "D": 1},
		"D": {"B": 5, "C": 1},
	}

	network := NewNetwork(nodes)
	
	// Initial path should be A->B->C->D
	path1, cost1, _ := network.FindShortestPath("A", "D")

	// Update link cost
	network.UpdateLink("B", "C", 10)

	// New path should be A->B->D
	path2, cost2, err := network.FindShortestPath("A", "D")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	if cost1 == cost2 {
		t.Error("Expected different costs after link update")
	}

	if equalPaths(path1, path2) {
		t.Error("Expected different paths after link update")
	}
}

func TestNoPathAvailable(t *testing.T) {
	nodes := map[string]map[string]int{
		"A": {"B": 1},
		"B": {"A": 1},
		"C": {"D": 1},
		"D": {"C": 1},
	}

	network := NewNetwork(nodes)
	
	_, _, err := network.FindShortestPath("A", "D")
	if err == nil {
		t.Error("Expected error when no path exists")
	}
}

func TestConcurrentAccess(t *testing.T) {
	nodes := map[string]map[string]int{
		"A": {"B": 1, "C": 4},
		"B": {"A": 1, "C": 2, "D": 5},
		"C": {"A": 4, "B": 2, "D": 1},
		"D": {"B": 5, "C": 1},
	}

	network := NewNetwork(nodes)
	
	done := make(chan bool)
	
	// Concurrent updates and queries
	go func() {
		for i := 0; i < 100; i++ {
			network.UpdateLink("B", "C", i%10+1)
			time.Sleep(time.Millisecond)
		}
		done <- true
	}()

	go func() {
		for i := 0; i < 100; i++ {
			network.FindShortestPath("A", "D")
			time.Sleep(time.Millisecond)
		}
		done <- true
	}()

	<-done
	<-done
}

func equalPaths(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}