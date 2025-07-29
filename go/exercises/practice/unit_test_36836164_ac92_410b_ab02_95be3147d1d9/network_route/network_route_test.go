package networkroute

import (
	"reflect"
	"testing"
)

func TestFindOptimalPath(t *testing.T) {
	tests := []struct {
		name          string
		nodes         []int
		edges         [][4]int
		source        int
		destination   int
		minBandwidth int
		maxLatency   int
		want         []int
	}{
		{
			name:          "basic path with sufficient bandwidth",
			nodes:         []int{0, 1, 2, 3},
			edges:         [][4]int{{0, 1, 10, 50}, {0, 2, 5, 20}, {1, 2, 3, 30}, {1, 3, 2, 40}, {2, 3, 1, 60}},
			source:        0,
			destination:   3,
			minBandwidth: 35,
			maxLatency:   15,
			want:         []int{0, 1, 3},
		},
		{
			name:          "no path meets bandwidth requirement",
			nodes:         []int{0, 1, 2, 3},
			edges:         [][4]int{{0, 1, 10, 30}, {0, 2, 5, 20}, {1, 3, 2, 25}},
			source:        0,
			destination:   3,
			minBandwidth: 35,
			maxLatency:   15,
			want:         []int{},
		},
		{
			name:          "no path meets latency requirement",
			nodes:         []int{0, 1, 2, 3},
			edges:         [][4]int{{0, 1, 10, 50}, {1, 3, 10, 40}},
			source:        0,
			destination:   3,
			minBandwidth: 35,
			maxLatency:   15,
			want:         []int{},
		},
		{
			name:          "multiple valid paths with same bandwidth",
			nodes:         []int{0, 1, 2, 3, 4},
			edges:         [][4]int{{0, 1, 5, 40}, {0, 2, 5, 40}, {1, 3, 5, 40}, {2, 3, 5, 40}, {3, 4, 5, 40}},
			source:        0,
			destination:   4,
			minBandwidth: 40,
			maxLatency:   20,
			want:         []int{0, 1, 3, 4}, // or any other valid path
		},
		{
			name:          "source equals destination",
			nodes:         []int{0, 1, 2},
			edges:         [][4]int{{0, 1, 10, 50}, {1, 2, 5, 30}},
			source:        0,
			destination:   0,
			minBandwidth: 10,
			maxLatency:   100,
			want:         []int{0},
		},
		{
			name:          "disconnected graph",
			nodes:         []int{0, 1, 2, 3},
			edges:         [][4]int{{0, 1, 5, 50}, {2, 3, 5, 50}},
			source:        0,
			destination:   3,
			minBandwidth: 10,
			maxLatency:   100,
			want:         []int{},
		},
		{
			name:          "zero bandwidth edge",
			nodes:         []int{0, 1, 2},
			edges:         [][4]int{{0, 1, 5, 50}, {1, 2, 5, 0}},
			source:        0,
			destination:   2,
			minBandwidth: 10,
			maxLatency:   100,
			want:         []int{},
		},
		{
			name:          "zero latency edge",
			nodes:         []int{0, 1, 2},
			edges:         [][4]int{{0, 1, 0, 50}, {1, 2, 0, 50}},
			source:        0,
			destination:   2,
			minBandwidth: 10,
			maxLatency:   0,
			want:         []int{0, 1, 2},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindOptimalPath(tt.nodes, tt.edges, tt.source, tt.destination, tt.minBandwidth, tt.maxLatency)
			
			// For cases where multiple valid paths exist, check if the result is valid
			if len(tt.want) > 0 || len(got) > 0 {
				if len(tt.want) == 0 && len(got) != 0 {
					t.Errorf("FindOptimalPath() = %v, want empty path", got)
				} else if len(tt.want) != 0 && len(got) == 0 {
					t.Errorf("FindOptimalPath() returned empty path, want %v", tt.want)
				} else if len(tt.want) > 0 {
					// Check path validity
					if got[0] != tt.source || got[len(got)-1] != tt.destination {
						t.Errorf("FindOptimalPath() path doesn't start/end correctly: got %v", got)
					}
					
					// For the basic test case, check exact match
					if tt.name == "basic path with sufficient bandwidth" && !reflect.DeepEqual(got, tt.want) {
						t.Errorf("FindOptimalPath() = %v, want %v", got, tt.want)
					}
				}
			}
		})
	}
}