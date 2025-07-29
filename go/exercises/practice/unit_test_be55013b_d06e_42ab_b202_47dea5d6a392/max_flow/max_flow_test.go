package max_flow

import (
	"errors"
	"testing"
)

func TestMaxFlow(t *testing.T) {
	tests := []struct {
		name        string
		n           int
		edges       []Edge
		source      int
		sink        int
		expected    int
		expectError bool
	}{
		{
			name:   "Basic flow network",
			n:      4,
			source: 0,
			sink:   3,
			edges: []Edge{
				{from: 0, to: 1, capacity: 3},
				{from: 0, to: 2, capacity: 2},
				{from: 1, to: 2, capacity: 1},
				{from: 1, to: 3, capacity: 3},
				{from: 2, to: 3, capacity: 2},
			},
			expected:    5,
			expectError: false,
		},
		{
			name:   "No path from source to sink",
			n:      4,
			source: 0,
			sink:   3,
			edges: []Edge{
				{from: 0, to: 1, capacity: 3},
				{from: 0, to: 2, capacity: 2},
				{from: 1, to: 2, capacity: 1},
				// No edge to sink (node 3)
			},
			expected:    0,
			expectError: false,
		},
		{
			name:   "Single path",
			n:      3,
			source: 0,
			sink:   2,
			edges: []Edge{
				{from: 0, to: 1, capacity: 2},
				{from: 1, to: 2, capacity: 2},
			},
			expected:    2,
			expectError: false,
		},
		{
			name:   "Multiple edges between same nodes",
			n:      3,
			source: 0,
			sink:   2,
			edges: []Edge{
				{from: 0, to: 1, capacity: 2},
				{from: 0, to: 1, capacity: 3},
				{from: 1, to: 2, capacity: 5},
			},
			expected:    5,
			expectError: false,
		},
		{
			name:   "Larger network",
			n:      6,
			source: 0,
			sink:   5,
			edges: []Edge{
				{from: 0, to: 1, capacity: 10},
				{from: 0, to: 2, capacity: 10},
				{from: 1, to: 2, capacity: 2},
				{from: 1, to: 3, capacity: 4},
				{from: 1, to: 4, capacity: 8},
				{from: 2, to: 4, capacity: 9},
				{from: 3, to: 5, capacity: 10},
				{from: 4, to: 3, capacity: 6},
				{from: 4, to: 5, capacity: 10},
			},
			expected:    19,
			expectError: false,
		},
		{
			name:   "Zero capacity edges",
			n:      3,
			source: 0,
			sink:   2,
			edges: []Edge{
				{from: 0, to: 1, capacity: 0},
				{from: 1, to: 2, capacity: 5},
			},
			expected:    0,
			expectError: false,
		},
		{
			name:   "Self-loops",
			n:      3,
			source: 0,
			sink:   2,
			edges: []Edge{
				{from: 0, to: 0, capacity: 10},
				{from: 0, to: 1, capacity: 5},
				{from: 1, to: 1, capacity: 10},
				{from: 1, to: 2, capacity: 5},
				{from: 2, to: 2, capacity: 10},
			},
			expected:    5,
			expectError: false,
		},
		{
			name:   "Negative capacity edge",
			n:      3,
			source: 0,
			sink:   2,
			edges: []Edge{
				{from: 0, to: 1, capacity: 5},
				{from: 1, to: 2, capacity: -1}, // Negative capacity
			},
			expected:    0,
			expectError: true,
		},
		{
			name:        "Source out of range",
			n:           3,
			source:      3, // Out of range
			sink:        2,
			edges:       []Edge{{from: 0, to: 1, capacity: 5}, {from: 1, to: 2, capacity: 5}},
			expected:    0,
			expectError: true,
		},
		{
			name:        "Sink out of range",
			n:           3,
			source:      0,
			sink:        3, // Out of range
			edges:       []Edge{{from: 0, to: 1, capacity: 5}, {from: 1, to: 2, capacity: 5}},
			expected:    0,
			expectError: true,
		},
		{
			name:        "Edge from node out of range",
			n:           3,
			source:      0,
			sink:        2,
			edges:       []Edge{{from: 3, to: 1, capacity: 5}, {from: 1, to: 2, capacity: 5}}, // from is out of range
			expected:    0,
			expectError: true,
		},
		{
			name:        "Edge to node out of range",
			n:           3,
			source:      0,
			sink:        2,
			edges:       []Edge{{from: 0, to: 3, capacity: 5}, {from: 1, to: 2, capacity: 5}}, // to is out of range
			expected:    0,
			expectError: true,
		},
		{
			name:   "Complex network with bottleneck",
			n:      7,
			source: 0,
			sink:   6,
			edges: []Edge{
				{from: 0, to: 1, capacity: 5},
				{from: 0, to: 2, capacity: 10},
				{from: 1, to: 3, capacity: 4},
				{from: 1, to: 4, capacity: 2},
				{from: 2, to: 3, capacity: 2},
				{from: 2, to: 4, capacity: 8},
				{from: 3, to: 5, capacity: 3},
				{from: 4, to: 5, capacity: 5},
				{from: 5, to: 6, capacity: 7},
			},
			expected:    7,
			expectError: false,
		},
		{
			name:   "Network with parallel paths",
			n:      4,
			source: 0,
			sink:   3,
			edges: []Edge{
				{from: 0, to: 1, capacity: 5},
				{from: 0, to: 2, capacity: 5},
				{from: 1, to: 3, capacity: 5},
				{from: 2, to: 3, capacity: 5},
			},
			expected:    10,
			expectError: false,
		},
		{
			name:   "Empty edge list",
			n:      3,
			source: 0,
			sink:   2,
			edges:  []Edge{},
			expected:    0,
			expectError: false,
		},
		{
			name:   "Same source and sink",
			n:      3,
			source: 1,
			sink:   1,
			edges: []Edge{
				{from: 0, to: 1, capacity: 5},
				{from: 1, to: 2, capacity: 5},
			},
			expected:    0,
			expectError: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			flow, err := MaxFlow(test.n, test.edges, test.source, test.sink)

			if test.expectError {
				if err == nil {
					t.Errorf("Expected an error but got none")
				}
			} else {
				if err != nil {
					t.Errorf("Unexpected error: %v", err)
				}
				if flow != test.expected {
					t.Errorf("Expected flow %d but got %d", test.expected, flow)
				}
			}
		})
	}
}

func TestLargeNetwork(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping large network test in short mode")
	}

	// Create a large network with 100 nodes and 1000 edges
	n := 100
	source := 0
	sink := n - 1
	edges := make([]Edge, 0, 1000)

	// Add edges in a grid-like pattern
	for i := 0; i < n-1; i++ {
		for j := 0; j < 10; j++ { // Each node connects to up to 10 others
			target := (i + j + 1) % n
			if target != i {
				edges = append(edges, Edge{from: i, to: target, capacity: (i*j)%10 + 1})
			}
		}
	}

	// This is just a smoke test to verify the algorithm doesn't crash or timeout on large inputs
	flow, err := MaxFlow(n, edges, source, sink)
	if err != nil {
		t.Errorf("Unexpected error on large network: %v", err)
	}
	if flow < 0 {
		t.Errorf("Flow should be non-negative, got %d", flow)
	}
}

func TestInvalidInputs(t *testing.T) {
	// Test with negative number of nodes
	_, err := MaxFlow(-1, []Edge{{from: 0, to: 1, capacity: 5}}, 0, 1)
	if err == nil {
		t.Errorf("Expected error for negative number of nodes but got none")
	}

	// Test with nil edges
	_, err = MaxFlow(3, nil, 0, 2)
	if err != nil {
		t.Errorf("Unexpected error for nil edges: %v", err)
	}

	// Test with negative source
	_, err = MaxFlow(3, []Edge{{from: 0, to: 1, capacity: 5}}, -1, 2)
	if err == nil {
		t.Errorf("Expected error for negative source but got none")
	}

	// Test with negative sink
	_, err = MaxFlow(3, []Edge{{from: 0, to: 1, capacity: 5}}, 0, -1)
	if err == nil {
		t.Errorf("Expected error for negative sink but got none")
	}
}

func BenchmarkMaxFlow(b *testing.B) {
	n := 50
	source := 0
	sink := n - 1
	edges := make([]Edge, 0, 500)

	// Create a dense network
	for i := 0; i < n-1; i++ {
		for j := i + 1; j < n; j++ {
			if (i+j)%5 == 0 { // Add some sparsity
				edges = append(edges, Edge{from: i, to: j, capacity: (i*j)%15 + 1})
			}
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = MaxFlow(n, edges, source, sink)
	}
}

func TestMaxFlowEdgeCases(t *testing.T) {
	// Test when source and sink are the only nodes
	n := 2
	source := 0
	sink := 1
	edges := []Edge{
		{from: 0, to: 1, capacity: 10},
	}
	flow, err := MaxFlow(n, edges, source, sink)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if flow != 10 {
		t.Errorf("Expected flow 10 but got %d", flow)
	}

	// Test when there are multiple direct edges from source to sink
	edges = []Edge{
		{from: 0, to: 1, capacity: 10},
		{from: 0, to: 1, capacity: 20},
	}
	flow, err = MaxFlow(n, edges, source, sink)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if flow != 30 {
		t.Errorf("Expected flow 30 but got %d", flow)
	}

	// Test with a single node (source = sink)
	n = 1
	source = 0
	sink = 0
	edges = []Edge{}
	flow, err = MaxFlow(n, edges, source, sink)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if flow != 0 {
		t.Errorf("Expected flow 0 but got %d", flow)
	}
}

func validateEdges(edges []Edge, n int) error {
	for _, edge := range edges {
		if edge.from < 0 || edge.from >= n {
			return errors.New("edge source out of range")
		}
		if edge.to < 0 || edge.to >= n {
			return errors.New("edge destination out of range")
		}
		if edge.capacity < 0 {
			return errors.New("negative capacity")
		}
	}
	return nil
}