package traffic_sim

import (
	"reflect"
	"testing"
)

func TestSimulateTraffic(t *testing.T) {
	tests := []struct {
		name               string
		network           map[string]map[string]int
		initialDistribution map[string]int
		steps             int
		wantTotalVehicles int
	}{
		{
			name: "simple two intersection network",
			network: map[string]map[string]int{
				"A": {"B": 5},
				"B": {"A": 5},
			},
			initialDistribution: map[string]int{
				"A": 10,
				"B": 0,
			},
			steps:             1,
			wantTotalVehicles: 10,
		},
		{
			name: "triangle network",
			network: map[string]map[string]int{
				"A": {"B": 3, "C": 2},
				"B": {"C": 4, "A": 3},
				"C": {"A": 2, "B": 4},
			},
			initialDistribution: map[string]int{
				"A": 5,
				"B": 3,
				"C": 2,
			},
			steps:             5,
			wantTotalVehicles: 10,
		},
		{
			name:   "empty network",
			network: map[string]map[string]int{},
			initialDistribution: map[string]int{},
			steps:             1,
			wantTotalVehicles: 0,
		},
		{
			name: "network with dead end",
			network: map[string]map[string]int{
				"A": {"B": 5},
				"B": {},
			},
			initialDistribution: map[string]int{
				"A": 3,
				"B": 2,
			},
			steps:             3,
			wantTotalVehicles: 5,
		},
		{
			name: "complex network with varying capacities",
			network: map[string]map[string]int{
				"A": {"B": 2, "C": 3, "D": 1},
				"B": {"A": 2, "C": 2, "E": 4},
				"C": {"A": 3, "B": 2, "D": 2, "E": 3},
				"D": {"A": 1, "C": 2, "E": 2},
				"E": {"B": 4, "C": 3, "D": 2},
			},
			initialDistribution: map[string]int{
				"A": 5,
				"B": 3,
				"C": 4,
				"D": 2,
				"E": 6,
			},
			steps:             10,
			wantTotalVehicles: 20,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := SimulateTraffic(tt.network, tt.initialDistribution, tt.steps)

			// Check if total number of vehicles is preserved
			totalVehicles := 0
			for _, count := range got {
				totalVehicles += count
			}
			if totalVehicles != tt.wantTotalVehicles {
				t.Errorf("SimulateTraffic() total vehicles = %v, want %v", totalVehicles, tt.wantTotalVehicles)
			}

			// Check if result contains all intersections
			for intersection := range tt.network {
				if _, exists := got[intersection]; !exists {
					t.Errorf("SimulateTraffic() missing intersection %v in result", intersection)
				}
			}
		})
	}
}

func TestSimulateTrafficEdgeCases(t *testing.T) {
	tests := []struct {
		name               string
		network           map[string]map[string]int
		initialDistribution map[string]int
		steps             int
		want              map[string]int
	}{
		{
			name:   "zero steps",
			network: map[string]map[string]int{
				"A": {"B": 1},
				"B": {"A": 1},
			},
			initialDistribution: map[string]int{
				"A": 2,
				"B": 3,
			},
			steps: 0,
			want: map[string]int{
				"A": 2,
				"B": 3,
			},
		},
		{
			name: "no capacity roads",
			network: map[string]map[string]int{
				"A": {"B": 0},
				"B": {"A": 0},
			},
			initialDistribution: map[string]int{
				"A": 5,
				"B": 5,
			},
			steps: 5,
			want: map[string]int{
				"A": 5,
				"B": 5,
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := SimulateTraffic(tt.network, tt.initialDistribution, tt.steps)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("SimulateTraffic() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkSimulateTraffic(b *testing.B) {
	network := map[string]map[string]int{
		"A": {"B": 10, "C": 15, "D": 5},
		"B": {"A": 10, "C": 8, "E": 12},
		"C": {"A": 15, "B": 8, "D": 7, "E": 9},
		"D": {"A": 5, "C": 7, "E": 6},
		"E": {"B": 12, "C": 9, "D": 6},
	}
	initialDistribution := map[string]int{
		"A": 20,
		"B": 15,
		"C": 25,
		"D": 10,
		"E": 30,
	}
	steps := 100

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		SimulateTraffic(network, initialDistribution, steps)
	}
}