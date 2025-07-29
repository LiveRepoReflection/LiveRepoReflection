package eventual_graph

import (
	"testing"
	"sync"
)

func TestFindNeighbors(t *testing.T) {
	graph := map[string]Node{
		"A": {ID: "A", Version: 1, Data: "DataA"},
		"B": {ID: "B", Version: 1, Data: "DataB"},
		"C": {ID: "C", Version: 1, Data: "DataC"},
	}
	edges := map[string][]string{
		"A": {"B"},
		"B": {"C"},
		"C": {"A"},
	}

	tests := []struct {
		name     string
		nodeID   string
		expected []string
	}{
		{"Node with one neighbor", "A", []string{"C"}},
		{"Node with one neighbor", "B", []string{"A"}},
		{"Node with one neighbor", "C", []string{"B"}},
		{"Node with no neighbors", "D", nil},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindNeighbors(graph, edges, tt.nodeID)
			if len(got) != len(tt.expected) {
				t.Errorf("FindNeighbors() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestPropagateUpdates(t *testing.T) {
	graph := map[string]Node{
		"A": {ID: "A", Version: 3, Data: "DataA"},
		"B": {ID: "B", Version: 1, Data: "DataB"},
		"C": {ID: "C", Version: 2, Data: "DataC"},
		"D": {ID: "D", Version: 1, Data: "DataD"},
	}
	edges := map[string][]string{
		"A": {"B", "C"},
		"B": {"D"},
		"C": {"D"},
	}

	var mu sync.Mutex

	tests := []struct {
		name           string
		source         string
		target         string
		maxNodesToSend int
		expectedError  bool
	}{
		{"Update from newer node", "A", "B", 3, false},
		{"Update from older node", "B", "A", 3, false},
		{"Non-existent source", "X", "A", 3, true},
		{"Non-existent target", "A", "X", 3, true},
		{"Limit nodes sent", "A", "D", 2, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mu.Lock()
			err := PropagateUpdates(graph, edges, tt.source, tt.target, tt.maxNodesToSend)
			mu.Unlock()

			if (err != nil) != tt.expectedError {
				t.Errorf("PropagateUpdates() error = %v, wantErr %v", err, tt.expectedError)
			}
		})
	}
}

func TestCycleDetection(t *testing.T) {
	graph := map[string]Node{
		"A": {ID: "A", Version: 2, Data: "DataA"},
		"B": {ID: "B", Version: 1, Data: "DataB"},
		"C": {ID: "C", Version: 1, Data: "DataC"},
	}
	edges := map[string][]string{
		"A": {"B"},
		"B": {"C"},
		"C": {"A"},
	}

	var mu sync.Mutex

	t.Run("Cycle doesn't cause infinite loop", func(t *testing.T) {
		mu.Lock()
		err := PropagateUpdates(graph, edges, "A", "C", 10)
		mu.Unlock()

		if err != nil {
			t.Errorf("PropagateUpdates() failed with cycle: %v", err)
		}
	})
}

func TestConcurrentUpdates(t *testing.T) {
	graph := map[string]Node{
		"A": {ID: "A", Version: 3, Data: "DataA"},
		"B": {ID: "B", Version: 1, Data: "DataB"},
		"C": {ID: "C", Version: 1, Data: "DataC"},
	}
	edges := map[string][]string{
		"A": {"B", "C"},
	}

	var wg sync.WaitGroup
	var mu sync.Mutex

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			mu.Lock()
			err := PropagateUpdates(graph, edges, "A", "B", 3)
			mu.Unlock()
			if err != nil {
				t.Errorf("Concurrent PropagateUpdates failed: %v", err)
			}
		}()
	}
	wg.Wait()
}