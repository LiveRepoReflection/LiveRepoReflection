package flight_itinerary

import (
	"testing"
)

func TestOptimalItinerary(t *testing.T) {
	tests := []struct {
		name     string
		N        int
		price    func(i, j, k int) int
		expected int
	}{
		{
			name: "SingleCity",
			N:    1,
			price: func(i, j, k int) int {
				// For a single city case, the cost is always zero.
				return 0
			},
			expected: 0,
		},
		{
			name: "ThreeCities_Static",
			N:    3,
			price: func(i, j, k int) int {
				// Define a dynamic pricing function: cost = 10*(i+j+k)
				return 10 * (i + j + k)
			},
			// For N=3, there are two possible itineraries:
			// Itinerary 1: 0 -> 1 -> 2 -> 0, cost = price(0,1,0) + price(1,2,1) + price(2,0,2)
			//           = 10*(0+1+0) + 10*(1+2+1) + 10*(2+0+2) = 10 + 40 + 40 = 90
			// Itinerary 2: 0 -> 2 -> 1 -> 0, cost = 10*(0+2+0) + 10*(2+1+1) + 10*(1+0+2) = 20 + 40 + 30 = 90
			// Expected minimum cost is 90.
			expected: 90,
		},
		{
			name: "FourCities_Matrix",
			N:    4,
			price: func(i, j, k int) int {
				// Create a static base cost matrix for the 4 cities.
				base := [][]int{
					{0, 10, 15, 20},
					{5, 0, 9, 10},
					{6, 13, 0, 12},
					{8, 8, 9, 0},
				}
				// The dynamic aspect: add an extra cost proportional to the number of cities already visited.
				return base[i][j] + 2*k
			},
			// For this test case, one optimal itinerary is:
			// 0 -> 1 -> 3 -> 2 -> 0 with cost breakdown:
			// price(0,1,0) = 10 + 0 = 10
			// price(1,3,1) = 10 + 2 = 12
			// price(3,2,2) = 9 + 4 = 13
			// price(2,0,3) = 6 + 6 = 12
			// Total cost = 10 + 12 + 13 + 12 = 47
			expected: 47,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := OptimalItinerary(tt.N, tt.price)
			if result != tt.expected {
				t.Errorf("OptimalItinerary(%d, price) = %d; want %d", tt.N, result, tt.expected)
			}
		})
	}
}

func BenchmarkOptimalItinerary(b *testing.B) {
	// Use the FourCities_Matrix test case for benchmarking.
	N := 4
	price := func(i, j, k int) int {
		base := [][]int{
			{0, 10, 15, 20},
			{5, 0, 9, 10},
			{6, 13, 0, 12},
			{8, 8, 9, 0},
		}
		return base[i][j] + 2*k
	}

	for i := 0; i < b.N; i++ {
		OptimalItinerary(N, price)
	}
}