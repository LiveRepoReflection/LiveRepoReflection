package networkrouter

import (
	"reflect"
	"testing"
)

func TestOptimizeNetwork(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			gotPaths, gotRejects := OptimizeNetwork(tc.graph, tc.requests)

			// Check if the paths match
			if !reflect.DeepEqual(gotPaths, tc.wantPaths) {
				t.Errorf("OptimizeNetwork() paths = %v, want %v", gotPaths, tc.wantPaths)
			}

			// Check if the rejected requests match
			if !reflect.DeepEqual(gotRejects, tc.wantRejects) {
				t.Errorf("OptimizeNetwork() rejected requests = %v, want %v", gotRejects, tc.wantRejects)
			}
		})
	}
}

func BenchmarkOptimizeNetwork(b *testing.B) {
	// Create a large test case for benchmarking
	largeGraph := NetworkGraph{
		Nodes: make([]Node, 100),
		Edges: make([]Edge, 1000),
	}
	
	// Initialize nodes
	for i := 0; i < 100; i++ {
		largeGraph.Nodes[i] = Node{ID: i + 1}
	}

	// Initialize edges (creating a dense graph)
	edgeIndex := 0
	for i := 1; i <= 100; i++ {
		for j := 1; j <= 10; j++ { // Each node connects to 10 other nodes
			dest := (i + j) % 100
			if dest == 0 {
				dest = 100
			}
			largeGraph.Edges[edgeIndex] = Edge{
				Source:      i,
				Destination: dest,
				Latency:    10,
				Bandwidth:  100,
			}
			edgeIndex++
		}
	}

	// Create test requests
	requests := make([]ContentRequest, 50)
	for i := 0; i < 50; i++ {
		requests[i] = ContentRequest{
			UserID:           i + 1,
			ContentID:        i + 1,
			SourceServer:     1,
			DestinationServer: 100,
			BandwidthRequired: 10,
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimizeNetwork(largeGraph, requests)
	}
}