package routeoptim

import (
	"testing"
	"time"
)

func TestRouteOptimizer(t *testing.T) {
	// Test case setup
	testCases := []struct {
		name            string
		nodes          int
		edges          []Edge
		requests       []DeliveryRequest
		vehicles       int
		expectedAccept int
	}{
		{
			name:   "Simple Path",
			nodes:  3,
			edges:  []Edge{{0, 1, 1}, {1, 2, 1}},
			vehicles: 1,
			requests: []DeliveryRequest{
				{
					Start:    0,
					End:      2,
					Deadline: time.Now().Add(10 * time.Second).Unix(),
				},
			},
			expectedAccept: 1,
		},
		{
			name:   "No Path Available",
			nodes:  3,
			edges:  []Edge{{0, 1, 1}},
			vehicles: 1,
			requests: []DeliveryRequest{
				{
					Start:    0,
					End:      2,
					Deadline: time.Now().Add(10 * time.Second).Unix(),
				},
			},
			expectedAccept: 0,
		},
		{
			name:   "Deadline Too Short",
			nodes:  2,
			edges:  []Edge{{0, 1, 100}},
			vehicles: 1,
			requests: []DeliveryRequest{
				{
					Start:    0,
					End:      1,
					Deadline: time.Now().Add(1 * time.Second).Unix(),
				},
			},
			expectedAccept: 0,
		},
		{
			name:   "Multiple Vehicles",
			nodes:  2,
			edges:  []Edge{{0, 1, 1}},
			vehicles: 2,
			requests: []DeliveryRequest{
				{
					Start:    0,
					End:      1,
					Deadline: time.Now().Add(10 * time.Second).Unix(),
				},
				{
					Start:    0,
					End:      1,
					Deadline: time.Now().Add(10 * time.Second).Unix(),
				},
			},
			expectedAccept: 2,
		},
		{
			name:   "Complex Graph",
			nodes:  5,
			edges:  []Edge{{0, 1, 1}, {1, 2, 2}, {2, 3, 1}, {3, 4, 2}, {0, 4, 10}, {1, 4, 5}},
			vehicles: 1,
			requests: []DeliveryRequest{
				{
					Start:    0,
					End:      4,
					Deadline: time.Now().Add(20 * time.Second).Unix(),
				},
			},
			expectedAccept: 1,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			optimizer := NewRouteOptimizer(tc.nodes, tc.edges, tc.vehicles)
			accepted := 0

			for _, req := range tc.requests {
				if optimizer.ProcessRequest(req) {
					accepted++
				}
			}

			if accepted != tc.expectedAccept {
				t.Errorf("Expected %d accepted requests, got %d", tc.expectedAccept, accepted)
			}
		})
	}
}

func TestLargeScale(t *testing.T) {
	// Generate large graph
	nodes := 10000
	edges := make([]Edge, 0)
	for i := 0; i < nodes-1; i++ {
		edges = append(edges, Edge{i, i + 1, 1})
	}

	optimizer := NewRouteOptimizer(nodes, edges, 100)

	// Test processing many requests
	deadline := time.Now().Add(1 * time.Hour).Unix()
	for i := 0; i < 1000; i++ {
		start := i % (nodes - 1)
		end := start + 1
		req := DeliveryRequest{
			Start:    start,
			End:      end,
			Deadline: deadline,
		}
		
		// Ensure request processing completes within reasonable time
		start_time := time.Now()
		optimizer.ProcessRequest(req)
		duration := time.Since(start_time)
		
		if duration > 100*time.Millisecond {
			t.Errorf("Request processing took too long: %v", duration)
		}
	}
}

func BenchmarkRouteOptimizer(b *testing.B) {
	// Setup benchmark graph
	nodes := 1000
	edges := make([]Edge, 0)
	for i := 0; i < nodes-1; i++ {
		edges = append(edges, Edge{i, i + 1, 1})
	}

	optimizer := NewRouteOptimizer(nodes, edges, 10)
	deadline := time.Now().Add(1 * time.Hour).Unix()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := DeliveryRequest{
			Start:    i % (nodes - 1),
			End:      (i % (nodes - 1)) + 1,
			Deadline: deadline,
		}
		optimizer.ProcessRequest(req)
	}
}