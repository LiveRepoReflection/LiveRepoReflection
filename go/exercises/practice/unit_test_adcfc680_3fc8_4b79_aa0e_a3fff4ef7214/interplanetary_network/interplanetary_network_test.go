package interplanetary_network

import (
	"math"
	"testing"
)

// mockDistance simulates the expensive distance calculation function
func mockDistance(planet1, planet2 int, time int64) float64 {
	// This is a mock implementation for testing
	// In real scenarios, this would be provided and be computationally expensive
	switch time {
	case 1:
		distances := map[[2]int]float64{
			{0, 1}: 1.0,
			{0, 2}: 2.0,
			{1, 2}: 1.5,
		}
		if planet1 > planet2 {
			planet1, planet2 = planet2, planet1
		}
		return distances[[2]int{planet1, planet2}]
	case 100:
		distances := map[[2]int]float64{
			{0, 1}: 5.5,
			{0, 2}: 2.1,
			{0, 3}: 3.2,
			{1, 2}: 4.5,
			{1, 3}: 1.2,
			{2, 3}: 3.0,
		}
		if planet1 > planet2 {
			planet1, planet2 = planet2, planet1
		}
		return distances[[2]int{planet1, planet2}]
	default:
		// Default case returns Euclidean distance based on planet numbers
		return math.Abs(float64(planet1 - planet2))
	}
}

func TestMinimumNetworkCost(t *testing.T) {
	tests := []struct {
		name       string
		n          int
		targetTime int64
		want       float64
	}{
		{
			name:       "Single Planet",
			n:          1,
			targetTime: 1,
			want:       0.0,
		},
		{
			name:       "Three Planets at Time 1",
			n:          3,
			targetTime: 1,
			want:       2.5, // Optimal connections: 0-1 (1.0) and 1-2 (1.5)
		},
		{
			name:       "Four Planets at Time 100",
			n:          4,
			targetTime: 100,
			want:       6.3, // Optimal connections: 1-3 (1.2), 0-2 (2.1), 2-3 (3.0)
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinimumNetworkCost(tt.n, tt.targetTime, mockDistance)
			if math.Abs(got-tt.want) > 1e-6 {
				t.Errorf("MinimumNetworkCost() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestDistanceFunctionCalls(t *testing.T) {
	callCount := 0
	wrappedDistance := func(planet1, planet2 int, time int64) float64 {
		callCount++
		return mockDistance(planet1, planet2, time)
	}

	// Test with 4 planets
	MinimumNetworkCost(4, 100, wrappedDistance)

	// For n=4, a naive solution would make 6 distance calls (all pairs)
	// A more optimized solution should make fewer calls
	maxAllowedCalls := 6 // This is the maximum acceptable number of calls
	if callCount > maxAllowedCalls {
		t.Errorf("Too many distance function calls: got %v, want <= %v", callCount, maxAllowedCalls)
	}
}

func TestEdgeCases(t *testing.T) {
	tests := []struct {
		name       string
		n          int
		targetTime int64
		want       float64
	}{
		{
			name:       "Two Planets",
			n:          2,
			targetTime: 1,
			want:       1.0,
		},
		{
			name:       "Large Time Value",
			n:          2,
			targetTime: 1000000000,
			want:       1.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinimumNetworkCost(tt.n, tt.targetTime, mockDistance)
			if math.Abs(got-tt.want) > 1e-6 {
				t.Errorf("MinimumNetworkCost() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMinimumNetworkCost(b *testing.B) {
	for i := 0; i < b.N; i++ {
		MinimumNetworkCost(4, 100, mockDistance)
	}
}