package flight_planner_test

import (
	"testing"

	"flight_planner"
)

type testCase struct {
	description string
	numCities   int
	flights     []flight_planner.Flight
	source      int
	dest        int
	passengers  int
	expected    int
}

func TestMinCost(t *testing.T) {
	testCases := []testCase{
		{
			description: "Basic route with two alternate paths",
			numCities:   4,
			flights: []flight_planner.Flight{
				{U: 0, V: 1, C: 10, K: 20, I: 1},
				{U: 0, V: 2, C: 15, K: 15, I: 2},
				{U: 1, V: 3, C: 30, K: 15, I: 2},
				{U: 2, V: 3, C: 12, K: 30, I: 1},
			},
			source:     0,
			dest:       3,
			passengers: 10,
			// Calculations:
			// Route 0->1->3: (10 + 10*1) + (30 + 10*2) = 20 + 50 = 70
			// Route 0->2->3: (15 + 10*2) + (12 + 10*1) = 35 + 22 = 57
			// Expected best cost is 57.
			expected: 57,
		},
		{
			description: "No route due to capacity constraints",
			numCities:   3,
			flights: []flight_planner.Flight{
				{U: 0, V: 1, C: 10, K: 5, I: 2},
				{U: 1, V: 2, C: 20, K: 5, I: 3},
			},
			source:     0,
			dest:       2,
			passengers: 10,
			// Even though a path exists, the capacity on each flight (5) is insufficient for 10 passengers.
			expected: -1,
		},
		{
			description: "Cycle in graph: best path avoids cycle",
			numCities:   4,
			flights: []flight_planner.Flight{
				{U: 0, V: 1, C: 5, K: 20, I: 1},
				{U: 1, V: 2, C: 5, K: 20, I: 1},
				{U: 2, V: 1, C: 1, K: 20, I: 5},
				{U: 2, V: 3, C: 10, K: 20, I: 2},
			},
			source:     0,
			dest:       3,
			passengers: 5,
			// Valid route: 0->1->2->3
			// Cost: (5 + 5*1) + (5 + 5*1) + (10 + 5*2) = 10 + 10 + 20 = 40
			expected: 40,
		},
		{
			description: "Direct flight is cheapest option",
			numCities:   3,
			flights: []flight_planner.Flight{
				{U: 0, V: 2, C: 50, K: 30, I: 1},
				{U: 0, V: 1, C: 10, K: 30, I: 2},
				{U: 1, V: 2, C: 30, K: 30, I: 3},
			},
			source:     0,
			dest:       2,
			passengers: 10,
			// Direct flight cost: 50 + 10*1 = 60
			// Indirect route: (10 + 10*2) + (30 + 10*3) = 30 + 60 = 90
			// Expected best cost is 60.
			expected: 60,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := flight_planner.MinCost(tc.numCities, tc.flights, tc.source, tc.dest, tc.passengers)
			if result != tc.expected {
				t.Fatalf("MinCost(%d, flights, %d, %d, %d) = %d, want %d",
					tc.numCities, tc.source, tc.dest, tc.passengers, result, tc.expected)
			}
		})
	}
}

func BenchmarkMinCost(b *testing.B) {
	flights := []flight_planner.Flight{
		{U: 0, V: 1, C: 10, K: 20, I: 1},
		{U: 0, V: 2, C: 15, K: 15, I: 2},
		{U: 1, V: 3, C: 30, K: 15, I: 2},
		{U: 2, V: 3, C: 12, K: 30, I: 1},
	}
	numCities := 4
	source := 0
	dest := 3
	passengers := 10

	for i := 0; i < b.N; i++ {
		_ = flight_planner.MinCost(numCities, flights, source, dest, passengers)
	}
}