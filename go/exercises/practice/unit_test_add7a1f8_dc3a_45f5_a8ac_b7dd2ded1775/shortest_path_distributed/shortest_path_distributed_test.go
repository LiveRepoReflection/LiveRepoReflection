package shortest_path_distributed_test

import (
	"sync"
	"testing"
	"time"

	"shortest_path_distributed"
)

var (
	mockGraph       map[int64][]int64
	mockFaultyNodes map[int64]bool
	mockMu          sync.RWMutex
)

// mockGetNeighbors simulates a network call to a remote machine to get neighbors of a node.
// It looks up the neighbor list in the mockGraph map and simulates latency.
func mockGetNeighbors(node int64) []int64 {
	// Simulate network latency.
	time.Sleep(10 * time.Millisecond)
	mockMu.RLock()
	defer mockMu.RUnlock()
	// If the node is marked as faulty, simulate unavailability by returning nil.
	if faulty, exists := mockFaultyNodes[node]; exists && faulty {
		return nil
	}
	neighbors, exists := mockGraph[node]
	if !exists {
		return []int64{}
	}
	return neighbors
}

// setUpMockGraph sets the global mockGraph and mockFaultyNodes maps for a test.
func setUpMockGraph(graph map[int64][]int64, faultyNodes map[int64]bool) {
	mockMu.Lock()
	defer mockMu.Unlock()
	mockGraph = graph
	mockFaultyNodes = faultyNodes
	// Inject the mock getNeighbors function into the package under test.
	shortest_path_distributed.SetNeighborFunction(mockGetNeighbors)
}

func TestSimplePath(t *testing.T) {
	// Graph: 1 -> 2 -> 3
	graph := map[int64][]int64{
		1: {2},
		2: {3},
		3: {},
	}
	setUpMockGraph(graph, map[int64]bool{})
	path := shortest_path_distributed.CalculateShortestPath(1, 3)
	expected := []int64{1, 2, 3}
	if !equalPath(path, expected) {
		t.Fatalf("TestSimplePath: got path %v, expected %v", path, expected)
	}
}

func TestNoPath(t *testing.T) {
	// Graph: 1 -> 2, 3 isolated.
	graph := map[int64][]int64{
		1: {2},
		2: {},
		3: {},
	}
	setUpMockGraph(graph, map[int64]bool{})
	path := shortest_path_distributed.CalculateShortestPath(1, 3)
	if len(path) != 0 {
		t.Fatalf("TestNoPath: expected no path, got %v", path)
	}
}

func TestCyclePath(t *testing.T) {
	// Graph with cycle: 1 -> 2 -> 3 -> 1, and 3 -> 4.
	graph := map[int64][]int64{
		1: {2},
		2: {3},
		3: {1, 4},
		4: {},
	}
	setUpMockGraph(graph, map[int64]bool{})
	path := shortest_path_distributed.CalculateShortestPath(1, 4)
	expected := []int64{1, 2, 3, 4}
	if !equalPath(path, expected) {
		t.Fatalf("TestCyclePath: got path %v, expected %v", path, expected)
	}
}

func TestMultipleShortestPaths(t *testing.T) {
	// Graph: 1 -> 2 -> 4 and 1 -> 3 -> 4
	graph := map[int64][]int64{
		1: {2, 3},
		2: {4},
		3: {4},
		4: {},
	}
	setUpMockGraph(graph, map[int64]bool{})
	path := shortest_path_distributed.CalculateShortestPath(1, 4)
	if len(path) != 3 {
		t.Fatalf("TestMultipleShortestPaths: expected a path length of 3, got %v", path)
	}
	if path[0] != 1 || path[len(path)-1] != 4 {
		t.Fatalf("TestMultipleShortestPaths: invalid start/end in path %v", path)
	}
	// Accept either [1,2,4] or [1,3,4]
	if !(equalPath(path, []int64{1, 2, 4}) || equalPath(path, []int64{1, 3, 4})) {
		t.Fatalf("TestMultipleShortestPaths: got unexpected path %v", path)
	}
}

func TestFaultTolerance(t *testing.T) {
	// Graph: 1 -> 2, 1 -> 3; 2 is faulty; 3 -> 4.
	graph := map[int64][]int64{
		1: {2, 3},
		2: {4},
		3: {4},
		4: {},
	}
	// Mark node 2 as faulty.
	faultyNodes := map[int64]bool{
		2: true,
	}
	setUpMockGraph(graph, faultyNodes)
	path := shortest_path_distributed.CalculateShortestPath(1, 4)
	expected := []int64{1, 3, 4}
	if !equalPath(path, expected) {
		t.Fatalf("TestFaultTolerance: got path %v, expected %v", path, expected)
	}
}

func TestConcurrentCalculations(t *testing.T) {
	// Create a larger graph for concurrent access:
	// 1 connects to nodes 2, 3, 4, 5. Each of these connect to 6.
	graph := map[int64][]int64{
		1: {2, 3, 4, 5},
		2: {6},
		3: {6},
		4: {6},
		5: {6},
		6: {},
	}
	setUpMockGraph(graph, map[int64]bool{})
	numRoutines := 10
	var wg sync.WaitGroup
	failCh := make(chan string, numRoutines)
	for i := 0; i < numRoutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			path := shortest_path_distributed.CalculateShortestPath(1, 6)
			// Expected path must be of length 3: 1 -> {2,3,4,5} -> 6
			if len(path) != 3 || path[0] != 1 || path[len(path)-1] != 6 {
				failCh <- "invalid path in concurrent calculation"
			}
		}()
	}
	wg.Wait()
	close(failCh)
	for f := range failCh {
		t.Fatal(f)
	}
}

// equalPath checks if two paths (slices of int64) are equal.
func equalPath(a, b []int64) bool {
	if len(a) != len(b) {
		return false
	}
	for i := 0; i < len(a); i++ {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}