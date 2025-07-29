package traffic_routing

import (
	"testing"
)

func TestTrafficRouting(t *testing.T) {
	tests := []struct {
		name      string
		n         int
		edges     []Edge
		requests  []Request
		expected  []map[string]interface{}
		wantError bool
	}{
		{
			name: "simple network with single request",
			n:    4,
			edges: []Edge{
				{0, 1, 10, 0},
				{1, 2, 5, 0},
				{0, 3, 8, 0},
				{3, 2, 6, 0},
			},
			requests: []Request{
				{0, 2, 7},
			},
			expected: []map[string]interface{}{
				{
					"paths": []PathFlow{
						{Path: []int{0, 1, 2}, Flow: 5},
						{Path: []int{0, 3, 2}, Flow: 2},
					},
				},
			},
			wantError: false,
		},
		{
			name: "network with insufficient capacity",
			n:    3,
			edges: []Edge{
				{0, 1, 5, 4},
				{1, 2, 3, 2},
			},
			requests: []Request{
				{0, 2, 4},
			},
			expected:  nil,
			wantError: true,
		},
		{
			name: "multiple requests with shared edges",
			n:    5,
			edges: []Edge{
				{0, 1, 10, 0},
				{1, 2, 8, 0},
				{0, 3, 12, 0},
				{3, 2, 10, 0},
				{2, 4, 15, 0},
			},
			requests: []Request{
				{0, 2, 10},
				{0, 4, 8},
			},
			expected: []map[string]interface{}{
				{
					"paths": []PathFlow{
						{Path: []int{0, 1, 2}, Flow: 8},
						{Path: []int{0, 3, 2}, Flow: 2},
					},
				},
				{
					"paths": []PathFlow{
						{Path: []int{0, 1, 2, 4}, Flow: 5},
						{Path: []int{0, 3, 2, 4}, Flow: 3},
					},
				},
			},
			wantError: false,
		},
		{
			name: "request with same source and destination",
			n:    2,
			edges: []Edge{
				{0, 1, 10, 0},
			},
			requests: []Request{
				{0, 0, 5},
			},
			expected: []map[string]interface{}{
				{
					"paths": []PathFlow{
						{Path: []int{0}, Flow: 5},
					},
				},
			},
			wantError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := RouteTraffic(tt.n, tt.edges, tt.requests)
			if (err != nil) != tt.wantError {
				t.Errorf("RouteTraffic() error = %v, wantError %v", err, tt.wantError)
				return
			}
			if !tt.wantError {
				if len(got) != len(tt.expected) {
					t.Errorf("RouteTraffic() result length = %d, want %d", len(got), len(tt.expected))
					return
				}
				// Additional validation of paths and flows would go here
			}
		})
	}
}

func BenchmarkTrafficRouting(b *testing.B) {
	n := 10
	edges := []Edge{
		{0, 1, 20, 0},
		{1, 2, 15, 0},
		{0, 3, 25, 0},
		{3, 2, 20, 0},
		{2, 4, 30, 0},
		{4, 5, 10, 0},
		{5, 6, 12, 0},
		{6, 7, 8, 0},
		{7, 8, 5, 0},
		{8, 9, 3, 0},
	}
	requests := []Request{
		{0, 2, 15},
		{0, 9, 10},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		RouteTraffic(n, edges, requests)
	}
}