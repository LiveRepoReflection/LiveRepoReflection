package route

import (
	"reflect"
	"testing"
)

func TestRouteNetwork(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		links    [][3]int
		queries  []string
		expected []int
	}{
		{
			name:  "Example test case",
			n:     4,
			links: [][3]int{{0, 1, 5}, {1, 2, 3}},
			queries: []string{
				"route 0 2",
				"add 2 3 2",
				"route 0 3",
				"remove 1 2",
				"route 0 3",
			},
			expected: []int{8, 10, -1},
		},
		{
			name:  "Empty network",
			n:     3,
			links: [][3]int{},
			queries: []string{
				"route 0 2",
				"add 0 1 1",
				"route 0 2",
				"add 1 2 2",
				"route 0 2",
			},
			expected: []int{-1, -1, 3},
		},
		{
			name:  "Complex network operations",
			n:     5,
			links: [][3]int{{0, 1, 1}, {1, 2, 2}, {2, 3, 3}, {3, 4, 4}},
			queries: []string{
				"route 0 4",
				"remove 2 3",
				"route 0 4",
				"add 1 3 5",
				"route 0 4",
				"add 0 4 15",
				"route 0 4",
			},
			expected: []int{10, -1, 10, 10},
		},
		{
			name:  "Duplicate operations",
			n:     3,
			links: [][3]int{{0, 1, 5}},
			queries: []string{
				"add 0 1 3", // Should be ignored (duplicate)
				"route 0 1",
				"remove 0 1",
				"route 0 1",
				"remove 0 1", // Should be ignored (already removed)
			},
			expected: []int{5, -1},
		},
		{
			name:  "Multiple paths",
			n:     4,
			links: [][3]int{{0, 1, 1}, {1, 2, 4}, {2, 3, 1}, {0, 2, 3}, {1, 3, 5}},
			queries: []string{
				"route 0 3",
				"remove 0 2",
				"route 0 3",
				"remove 1 3",
				"route 0 3",
			},
			expected: []int{4, 6, 6},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			network := New(tt.n)
			for _, link := range tt.links {
				network.AddLink(link[0], link[1], link[2])
			}

			var results []int
			for _, query := range tt.queries {
				result := network.ProcessQuery(query)
				if result != nil {
					results = append(results, *result)
				}
			}

			if !reflect.DeepEqual(results, tt.expected) {
				t.Errorf("got %v, want %v", results, tt.expected)
			}
		})
	}
}

func BenchmarkRouteNetwork(b *testing.B) {
	// Create a medium-sized network for benchmarking
	n := 100
	network := New(n)
	
	// Add some initial links
	for i := 0; i < n-1; i++ {
		network.AddLink(i, i+1, i+1)
	}

	queries := []string{
		"route 0 99",
		"remove 50 51",
		"route 0 99",
		"add 50 51 50",
		"route 0 99",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for _, query := range queries {
			network.ProcessQuery(query)
		}
	}
}
