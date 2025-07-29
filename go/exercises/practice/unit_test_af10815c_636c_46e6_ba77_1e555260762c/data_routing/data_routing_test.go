package data_routing

import (
	"testing"
)

func TestFindOptimalPath(t *testing.T) {
	tests := []struct {
		name        string
		network     map[int]map[int]int
		bandwidth   map[int]map[int]int
		source      tuple
		destination tuple
		want        []int
	}{
		{
			name: "simple direct connection",
			network: map[int]map[int]int{
				1: {2: 10},
				2: {1: 10},
			},
			bandwidth: map[int]map[int]int{
				1: {2: 100},
				2: {1: 100},
			},
			source:      tuple{1, 101},
			destination: tuple{2, 201},
			want:        []int{1, 2},
		},
		{
			name: "multiple paths with congestion",
			network: map[int]map[int]int{
				1: {2: 10, 3: 20},
				2: {1: 10, 3: 30, 4: 5},
				3: {1: 20, 2: 30, 4: 15},
				4: {2: 5, 3: 15},
			},
			bandwidth: map[int]map[int]int{
				1: {2: 100, 3: 50},
				2: {1: 100, 3: 75, 4: 200},
				3: {1: 50, 2: 75, 4: 150},
				4: {2: 200, 3: 150},
			},
			source:      tuple{1, 101},
			destination: tuple{4, 401},
			want:        []int{1, 2, 4}, // Assuming GetCongestionLatency favors this path
		},
		{
			name: "no connection",
			network: map[int]map[int]int{
				1: {2: 10},
				2: {1: 10},
				3: {4: 5},
				4: {3: 5},
			},
			bandwidth: map[int]map[int]int{
				1: {2: 100},
				2: {1: 100},
				3: {4: 100},
				4: {3: 100},
			},
			source:      tuple{1, 101},
			destination: tuple{4, 401},
			want:        []int{},
		},
		{
			name: "complex network with multiple hops",
			network: map[int]map[int]int{
				1: {2: 5, 3: 10},
				2: {1: 5, 4: 8, 5: 2},
				3: {1: 10, 5: 1},
				4: {2: 8, 6: 3},
				5: {2: 2, 3: 1, 6: 4},
				6: {4: 3, 5: 4},
			},
			bandwidth: map[int]map[int]int{
				1: {2: 100, 3: 50},
				2: {1: 100, 4: 80, 5: 200},
				3: {1: 50, 5: 100},
				4: {2: 80, 6: 300},
				5: {2: 200, 3: 100, 6: 400},
				6: {4: 300, 5: 400},
			},
			source:      tuple{1, 101},
			destination: tuple{6, 601},
			want:        []int{1, 2, 5, 6}, // Assuming GetCongestionLatency favors this path
		},
	}

	// Mock GetCongestionLatency function for testing
	originalGetCongestionLatency := GetCongestionLatency
	defer func() { GetCongestionLatency = originalGetCongestionLatency }()
	GetCongestionLatency = func(dataCenterID int, path []int) int {
		// Simple congestion model: higher congestion for more hops
		return len(path) * 2
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := FindOptimalPath(tt.network, tt.bandwidth, tt.source, tt.destination)
			if len(got) != len(tt.want) {
				t.Errorf("FindOptimalPath() = %v, want %v", got, tt.want)
				return
			}
			for i := range got {
				if got[i] != tt.want[i] {
					t.Errorf("FindOptimalPath() = %v, want %v", got, tt.want)
					break
				}
			}
		})
	}
}

func BenchmarkFindOptimalPath(b *testing.B) {
	network := map[int]map[int]int{
		1: {2: 10, 3: 20, 4: 15},
		2: {1: 10, 3: 30, 4: 5},
		3: {1: 20, 2: 30, 4: 15, 5: 10},
		4: {1: 15, 2: 5, 3: 15, 5: 20},
		5: {3: 10, 4: 20, 6: 5},
		6: {5: 5, 7: 10},
		7: {6: 10, 8: 8},
		8: {7: 8, 9: 6},
		9: {8: 6, 10: 4},
		10: {9: 4},
	}

	bandwidth := map[int]map[int]int{
		1: {2: 100, 3: 50, 4: 75},
		2: {1: 100, 3: 75, 4: 200},
		3: {1: 50, 2: 75, 4: 150, 5: 100},
		4: {1: 75, 2: 200, 3: 150, 5: 300},
		5: {3: 100, 4: 300, 6: 500},
		6: {5: 500, 7: 400},
		7: {6: 400, 8: 600},
		8: {7: 600, 9: 700},
		9: {8: 700, 10: 800},
		10: {9: 800},
	}

	source := tuple{1, 101}
	destination := tuple{10, 1001}

	// Reset the benchmark timer
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		FindOptimalPath(network, bandwidth, source, destination)
	}
}