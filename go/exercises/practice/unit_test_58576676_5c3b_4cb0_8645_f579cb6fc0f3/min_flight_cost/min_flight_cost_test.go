package min_flight_cost

import (
	"testing"
	"time"
)

func TestMinFlightCost(t *testing.T) {
	tests := []struct {
		name         string
		n            int
		flights      [][]int
		src          int
		dst          int
		startTime    int64
		maxLayover   int
		maxFlights   int
		expectedCost int
	}{
		{
			name: "direct flight available",
			n:    3,
			flights: [][]int{
				{0, 1, 10, 20, 100},
				{1, 2, 30, 40, 200},
				{0, 2, 10, 50, 350},
			},
			src:          0,
			dst:          2,
			startTime:    5,
			maxLayover:   15,
			maxFlights:   2,
			expectedCost: 300,
		},
		{
			name: "no valid route",
			n:    3,
			flights: [][]int{
				{0, 1, 10, 20, 100},
				{1, 2, 30, 40, 200},
			},
			src:          0,
			dst:          2,
			startTime:    50,
			maxLayover:   5,
			maxFlights:   2,
			expectedCost: -1,
		},
		{
			name: "same source and destination",
			n:    3,
			flights: [][]int{
				{0, 1, 10, 20, 100},
				{1, 2, 30, 40, 200},
			},
			src:          0,
			dst:          0,
			startTime:    0,
			maxLayover:   0,
			maxFlights:   0,
			expectedCost: 0,
		},
		{
			name: "multiple layovers",
			n:    4,
			flights: [][]int{
				{0, 1, 100, 200, 50},
				{1, 2, 300, 400, 60},
				{2, 3, 500, 600, 70},
				{0, 3, 100, 700, 300},
			},
			src:          0,
			dst:          3,
			startTime:    0,
			maxLayover:   100,
			maxFlights:   3,
			expectedCost: 180,
		},
		{
			name: "max flights constraint",
			n:    4,
			flights: [][]int{
				{0, 1, 100, 200, 50},
				{1, 2, 300, 400, 60},
				{2, 3, 500, 600, 70},
				{0, 3, 100, 700, 300},
			},
			src:          0,
			dst:          3,
			startTime:    0,
			maxLayover:   100,
			maxFlights:   2,
			expectedCost: 300,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinFlightCost(tt.n, tt.flights, tt.src, tt.dst, tt.startTime, tt.maxLayover, tt.maxFlights)
			if got != tt.expectedCost {
				t.Errorf("MinFlightCost() = %v, want %v", got, tt.expectedCost)
			}
		})
	}
}

func BenchmarkMinFlightCost(b *testing.B) {
	n := 100
	flights := make([][]int, 0)
	now := time.Now().Unix()
	for i := 0; i < 1000; i++ {
		src := i % n
		dst := (i + 1) % n
		departure := now + int64(i*100)
		arrival := departure + 50
		cost := (i % 100) + 1
		flights = append(flights, []int{src, dst, int(departure), int(arrival), cost})
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinFlightCost(n, flights, 0, n-1, now, 3600, 5)
	}
}