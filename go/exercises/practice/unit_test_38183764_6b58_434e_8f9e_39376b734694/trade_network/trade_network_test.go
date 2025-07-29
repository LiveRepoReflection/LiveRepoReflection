package trade_network

import (
	"testing"
)

type testCase struct {
	name         string
	numPlanets   int
	numGoods     int
	demandSupply [][]int
	wormholes    [][]int
	penalty      int
	expected     int
}

func TestMinCostTrade(t *testing.T) {
	testCases := []testCase{
		{
			name:       "Simple trade",
			numPlanets: 3,
			numGoods:   1,
			// Planet 0 supplies 5 units, Planet 1 demands 5 units, Planet 2 is neutral.
			demandSupply: [][]int{
				{-5},
				{5},
				{0},
			},
			// One wormhole from planet 0 to 1 with cost 2 and capacity 5 for the single good.
			wormholes: [][]int{
				{0, 1, 2, 5},
			},
			penalty:  100,
			expected: 10, // 5 units * cost 2 = 10
		},
		{
			name:       "Insufficient capacity trade",
			numPlanets: 2,
			numGoods:   1,
			// Planet 0 supplies 5 units, Planet 1 demands 5 units.
			demandSupply: [][]int{
				{-5},
				{5},
			},
			// Single wormhole from planet 0 to 1 with capacity 3 and cost 1.
			wormholes: [][]int{
				{0, 1, 1, 3},
			},
			penalty:  100,
			// Only 3 units can be transported: cost=3, 2 units unmet => penalty=2*100=200, total = 203.
			expected: 203,
		},
		{
			name:       "Multiple goods trade",
			numPlanets: 2,
			numGoods:   2,
			// Planet 0 supplies 10 units of good0 and 5 units of good1, Planet 1 demands corresponding amounts.
			demandSupply: [][]int{
				{-10, -5},
				{10, 5},
			},
			// One wormhole from planet 0 to 1 with cost = 1.
			// Capacities: good0 capacity = 5, good1 capacity = 10.
			wormholes: [][]int{
				{0, 1, 1, 5, 10},
			},
			penalty: 10,
			// Good0: 5 units shipped (5*1=5) and 5 units unmet (5*10=50).
			// Good1: 5 units shipped (5*1=5).
			// Total cost = 5 + 50 + 5 = 60.
			expected: 60,
		},
		{
			name:       "Multiple routes",
			numPlanets: 3,
			numGoods:   1,
			// Planet 0 supplies 6 units, Planet 1 supplies 4 units, Planet 2 demands 10 units.
			demandSupply: [][]int{
				{-6},
				{-4},
				{10},
			},
			// Wormholes:
			// Direct: from 0 to 2: cost 2, capacity 6.
			// Direct: from 1 to 2: cost 2, capacity 4.
			// Alternative route: from 0 to 1: cost 1, capacity 2 and from 1 to 2: cost 3, capacity 2.
			// The optimal solution is to use the direct routes.
			wormholes: [][]int{
				{0, 2, 2, 6},
				{1, 2, 2, 4},
				{0, 1, 1, 2},
				{1, 2, 3, 2},
			},
			penalty:  100,
			// Optimal: Directly transport 6 units from 0->2 (cost: 6*2=12) and 4 units from 1->2 (cost: 4*2=8), total = 20.
			expected: 20,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := MinCostTrade(tc.numPlanets, tc.numGoods, tc.demandSupply, tc.wormholes, tc.penalty)
			if result != tc.expected {
				t.Fatalf("Test case '%s' failed: expected %d, got %d", tc.name, tc.expected, result)
			}
		})
	}
}

func BenchmarkMinCostTrade(b *testing.B) {
	// Using the Multiple routes test case for benchmarking.
	tc := testCase{
		name:       "Benchmark Multiple routes",
		numPlanets: 3,
		numGoods:   1,
		demandSupply: [][]int{
			{-6},
			{-4},
			{10},
		},
		wormholes: [][]int{
			{0, 2, 2, 6},
			{1, 2, 2, 4},
			{0, 1, 1, 2},
			{1, 2, 3, 2},
		},
		penalty:  100,
		expected: 20,
	}

	for i := 0; i < b.N; i++ {
		_ = MinCostTrade(tc.numPlanets, tc.numGoods, tc.demandSupply, tc.wormholes, tc.penalty)
	}
}