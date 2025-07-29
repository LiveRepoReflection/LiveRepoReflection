package dynamic_paths

import (
	"sync"
	"testing"
)

// The following tests assume the existence of a Graph struct with the methods:
//   NewGraph() *Graph
//   UpdateEdge(u int, v int, newTravelTime int)
//   QueryShortestPath(sources []int, destination int) int
// 
// The tests validate the graph's dynamic update and query functionalities.

func TestEmptyGraph(t *testing.T) {
	g := NewGraph()
	sources := []int{1, 2, 3}
	destination := 5
	result := g.QueryShortestPath(sources, destination)
	if result != -1 {
		t.Errorf("TestEmptyGraph: expected -1 for empty graph, got %d", result)
	}
}

func TestSingleEdge(t *testing.T) {
	g := NewGraph()
	// Add an edge 1->2 with travel time 10.
	g.UpdateEdge(1, 2, 10)
	
	// Query from source 1 to destination 2.
	result := g.QueryShortestPath([]int{1}, 2)
	if result != 10 {
		t.Errorf("TestSingleEdge: expected 10, got %d", result)
	}

	// Query from a non-connected source.
	result = g.QueryShortestPath([]int{3}, 2)
	if result != -1 {
		t.Errorf("TestSingleEdge: expected -1 for non-connected source, got %d", result)
	}
}

func TestMultipleSources(t *testing.T) {
	g := NewGraph()
	// Construct the following edges:
	// 1->4 (5), 2->4 (7), 3->4 (3)
	g.UpdateEdge(1, 4, 5)
	g.UpdateEdge(2, 4, 7)
	g.UpdateEdge(3, 4, 3)

	// Query from multiple sources to destination 4. Expected shortest path is 3.
	result := g.QueryShortestPath([]int{1, 2, 3}, 4)
	if result != 3 {
		t.Errorf("TestMultipleSources: expected 3, got %d", result)
	}
}

func TestUpdateEdgeRemoval(t *testing.T) {
	g := NewGraph()
	// Construct a simple path 1->2 (10) then 2->3 (20)
	g.UpdateEdge(1, 2, 10)
	g.UpdateEdge(2, 3, 20)

	// Query shortest path from 1 to 3. Expected path length is 30.
	result := g.QueryShortestPath([]int{1}, 3)
	if result != 30 {
		t.Errorf("TestUpdateEdgeRemoval: expected 30, got %d", result)
	}

	// Remove edge 2->3 by providing a negative travel time.
	g.UpdateEdge(2, 3, -1)
	result = g.QueryShortestPath([]int{1}, 3)
	if result != -1 {
		t.Errorf("TestUpdateEdgeRemoval: expected -1 after edge removal, got %d", result)
	}
}

func TestDynamicUpdates(t *testing.T) {
	g := NewGraph()
	// Build the following graph:
	// 1->2 (4), 2->3 (6), 1->3 (15)
	g.UpdateEdge(1, 2, 4)
	g.UpdateEdge(2, 3, 6)
	g.UpdateEdge(1, 3, 15)

	// Initially, the shortest path from 1 to 3 should be 10 (1->2->3).
	result := g.QueryShortestPath([]int{1}, 3)
	if result != 10 {
		t.Errorf("TestDynamicUpdates: expected 10, got %d", result)
	}

	// Update edge 1->3 to have a travel time of 5. Now, the direct path should be shorter.
	g.UpdateEdge(1, 3, 5)
	result = g.QueryShortestPath([]int{1}, 3)
	if result != 5 {
		t.Errorf("TestDynamicUpdates: expected 5 after update, got %d", result)
	}
}

func TestConcurrentAccess(t *testing.T) {
	g := NewGraph()
	// Build a simple chain graph: 0->1->2-> ... ->1000, each with travel time 1.
	numEdges := 1000
	for i := 0; i < numEdges; i++ {
		g.UpdateEdge(i, i+1, 1)
	}

	var wg sync.WaitGroup

	// Function to perform updates concurrently.
	updateFunc := func(start int) {
		defer wg.Done()
		for i := start; i < start+100 && i < numEdges; i++ {
			// Update: Increase travel time by 1.
			g.UpdateEdge(i, i+1, 2)
		}
	}

	// Function to perform queries concurrently.
	queryFunc := func(source int) {
		defer wg.Done()
		res := g.QueryShortestPath([]int{source}, numEdges)
		if res < 0 {
			t.Errorf("TestConcurrentAccess: expected valid path from %d to %d, got %d", source, numEdges, res)
		}
	}

	// Launch several goroutines for updating edges concurrently.
	for start := 0; start < numEdges; start += 100 {
		wg.Add(1)
		go updateFunc(start)
	}

	// Launch several goroutines for querying concurrently.
	for source := 0; source < numEdges; source += 100 {
		wg.Add(1)
		go queryFunc(source)
	}

	wg.Wait()
}