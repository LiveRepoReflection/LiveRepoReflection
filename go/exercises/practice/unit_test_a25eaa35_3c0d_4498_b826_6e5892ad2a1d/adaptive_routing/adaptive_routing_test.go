package adaptive_routing

import (
	"fmt"
	"sync"
	"testing"
)

func TestAdaptiveRouter(t *testing.T) {
	t.Run("Basic path finding", func(t *testing.T) {
		router := NewAdaptiveRouter()

		// Add nodes
		router.AddNode(1)
		router.AddNode(2)
		router.AddNode(3)

		// Add links
		router.AddLink(1, 2)
		router.AddLink(2, 3)

		// Find path from 1 to 3
		path, err := router.FindShortestPath(1, 3)
		if err != nil {
			t.Fatalf("Expected to find path, got error: %v", err)
		}
		assertPath(t, path, []int{1, 2, 3})

		// No direct path from 3 to 1 (directed graph)
		_, err = router.FindShortestPath(3, 1)
		if err == nil {
			t.Fatalf("Expected no path from 3 to 1, but found one")
		}
	})

	t.Run("Path after adding links", func(t *testing.T) {
		router := NewAdaptiveRouter()

		router.AddNode(1)
		router.AddNode(2)
		router.AddNode(3)
		router.AddNode(4)

		router.AddLink(1, 2)
		router.AddLink(2, 4)

		// Initially no path from 1 to 3
		_, err := router.FindShortestPath(1, 3)
		if err == nil {
			t.Fatalf("Expected no path from 1 to 3, but found one")
		}

		// Add link and check path
		router.AddLink(2, 3)
		path, err := router.FindShortestPath(1, 3)
		if err != nil {
			t.Fatalf("Expected to find path after adding link, got error: %v", err)
		}
		assertPath(t, path, []int{1, 2, 3})
	})

	t.Run("Path after removing links", func(t *testing.T) {
		router := NewAdaptiveRouter()

		router.AddNode(1)
		router.AddNode(2)
		router.AddNode(3)
		router.AddNode(4)

		router.AddLink(1, 2)
		router.AddLink(2, 3)
		router.AddLink(3, 4)

		// Initially there's a path from 1 to 4
		path, err := router.FindShortestPath(1, 4)
		if err != nil {
			t.Fatalf("Expected to find path, got error: %v", err)
		}
		assertPath(t, path, []int{1, 2, 3, 4})

		// Remove link and check path
		router.RemoveLink(2, 3)
		_, err = router.FindShortestPath(1, 4)
		if err == nil {
			t.Fatalf("Expected no path after removing link, but found one")
		}
	})

	t.Run("Path after removing nodes", func(t *testing.T) {
		router := NewAdaptiveRouter()

		for i := 1; i <= 5; i++ {
			router.AddNode(i)
		}

		router.AddLink(1, 2)
		router.AddLink(2, 3)
		router.AddLink(3, 4)
		router.AddLink(4, 5)

		// Initially there's a path from 1 to 5
		path, err := router.FindShortestPath(1, 5)
		if err != nil {
			t.Fatalf("Expected to find path, got error: %v", err)
		}
		assertPath(t, path, []int{1, 2, 3, 4, 5})

		// Remove node and check path
		router.RemoveNode(3)
		_, err = router.FindShortestPath(1, 5)
		if err == nil {
			t.Fatalf("Expected no path after removing node, but found one")
		}

		// Add alternate path
		router.AddLink(2, 4)
		path, err = router.FindShortestPath(1, 5)
		if err != nil {
			t.Fatalf("Expected to find new path, got error: %v", err)
		}
		assertPath(t, path, []int{1, 2, 4, 5})
	})

	t.Run("Multiple paths with different lengths", func(t *testing.T) {
		router := NewAdaptiveRouter()

		for i := 1; i <= 5; i++ {
			router.AddNode(i)
		}

		// Create two paths: 1->2->3->5 and 1->4->5
		router.AddLink(1, 2)
		router.AddLink(2, 3)
		router.AddLink(3, 5)
		router.AddLink(1, 4)
		router.AddLink(4, 5)

		// Should choose the shorter path
		path, err := router.FindShortestPath(1, 5)
		if err != nil {
			t.Fatalf("Expected to find path, got error: %v", err)
		}
		assertPath(t, path, []int{1, 4, 5})
	})

	t.Run("Network with cycles", func(t *testing.T) {
		router := NewAdaptiveRouter()

		for i := 1; i <= 4; i++ {
			router.AddNode(i)
		}

		// Create a cycle
		router.AddLink(1, 2)
		router.AddLink(2, 3)
		router.AddLink(3, 4)
		router.AddLink(4, 2)

		path, err := router.FindShortestPath(1, 4)
		if err != nil {
			t.Fatalf("Expected to find path in graph with cycle, got error: %v", err)
		}
		assertPath(t, path, []int{1, 2, 3, 4})
	})

	t.Run("Handle non-existent nodes", func(t *testing.T) {
		router := NewAdaptiveRouter()

		router.AddNode(1)
		router.AddNode(2)

		// Query for non-existent node
		_, err := router.FindShortestPath(1, 3)
		if err == nil {
			t.Fatalf("Expected error for non-existent destination node, got none")
		}

		_, err = router.FindShortestPath(3, 1)
		if err == nil {
			t.Fatalf("Expected error for non-existent source node, got none")
		}
	})

	t.Run("Large network test", func(t *testing.T) {
		router := NewAdaptiveRouter()

		// Create a larger network
		for i := 1; i <= 100; i++ {
			router.AddNode(i)
		}

		// Add some links
		for i := 1; i < 100; i++ {
			router.AddLink(i, i+1)
		}

		// Find path from 1 to 100
		path, err := router.FindShortestPath(1, 100)
		if err != nil {
			t.Fatalf("Expected to find path in large network, got error: %v", err)
		}
		if len(path) != 100 {
			t.Fatalf("Expected path of length 100, got %d", len(path))
		}
	})

	t.Run("Concurrency test", func(t *testing.T) {
		router := NewAdaptiveRouter()

		// Create a network
		for i := 1; i <= 20; i++ {
			router.AddNode(i)
		}

		// Create a path
		for i := 1; i < 20; i++ {
			router.AddLink(i, i+1)
		}

		var wg sync.WaitGroup
		errors := make(chan error, 100)

		// Launch goroutines to concurrently query and modify the network
		for i := 0; i < 10; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for j := 0; j < 10; j++ {
					// Query for paths
					_, err := router.FindShortestPath(1, 20)
					if err != nil {
						errors <- fmt.Errorf("query error: %v", err)
						return
					}
				}
			}()
		}

		for i := 0; i < 5; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for j := 0; j < 5; j++ {
					// Modify the network
					router.AddNode(100 + j)
					router.AddLink(20, 100+j)
					router.RemoveLink(20, 100+j)
					router.RemoveNode(100 + j)
				}
			}()
		}

		// Wait for all goroutines to complete
		wg.Wait()
		close(errors)

		// Check if there were any errors
		for err := range errors {
			t.Errorf("Concurrent operations error: %v", err)
		}
	})
}

func assertPath(t *testing.T, actual []int, expected []int) {
	t.Helper()
	if len(actual) != len(expected) {
		t.Fatalf("Expected path length %d, got %d", len(expected), len(actual))
	}
	for i, v := range expected {
		if actual[i] != v {
			t.Fatalf("Path mismatch at position %d: expected %d, got %d", i, v, actual[i])
		}
	}
}

func BenchmarkAddNode(b *testing.B) {
	router := NewAdaptiveRouter()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		router.AddNode(i)
	}
}

func BenchmarkAddLink(b *testing.B) {
	router := NewAdaptiveRouter()
	
	// Add a bunch of nodes first
	for i := 0; i < 1000; i++ {
		router.AddNode(i)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		src := i % 1000
		dst := (i + 1) % 1000
		router.AddLink(src, dst)
	}
}

func BenchmarkPathFinding(b *testing.B) {
	router := NewAdaptiveRouter()
	
	// Create a connected graph
	for i := 0; i < 1000; i++ {
		router.AddNode(i)
	}
	for i := 0; i < 999; i++ {
		router.AddLink(i, i+1)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		start := i % 500
		end := start + 500
		router.FindShortestPath(start, end)
	}
}

func BenchmarkUpdateAndQuery(b *testing.B) {
	router := NewAdaptiveRouter()
	
	// Create an initial network
	for i := 0; i < 1000; i++ {
		router.AddNode(i)
	}
	for i := 0; i < 999; i++ {
		router.AddLink(i, i+1)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if i%2 == 0 {
			// Perform an update
			src := i % 998
			router.RemoveLink(src, src+1)
			router.AddLink(src, src+1)
		} else {
			// Perform a query
			start := i % 500
			end := start + 300
			router.FindShortestPath(start, end)
		}
	}
}