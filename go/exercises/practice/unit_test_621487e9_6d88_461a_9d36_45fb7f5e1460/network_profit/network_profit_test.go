package network_profit

import (
	"reflect"
	"testing"
)

func TestMaxNetworkProfit(t *testing.T) {
	type testCase struct {
		name      string
		N         int
		profits   [][]int
		minCities int
		maxCities int
		budget    int
		costs     [][]int
		expected  int
	}
	
	testCases := []testCase{
		{
			name: "Three cities full network with spanning tree",
			N:    3,
			profits: [][]int{
				{0, 4, 5},
				{4, 0, 6},
				{5, 6, 0},
			},
			costs: [][]int{
				{0, 2, 3},
				{2, 0, 2},
				{3, 2, 0},
			},
			minCities: 2,
			maxCities: 3,
			budget:    5,
			// Explanation:
			// The best option is connecting all three nodes with edges (0,2) and (1,2) for a cost 3+2=5 and profit 5+6=11.
			expected: 11,
		},
		{
			name: "Three cities limited by budget",
			N:    3,
			profits: [][]int{
				{0, 3, -1},
				{3, 0, 2},
				{-1, 2, 0},
			},
			costs: [][]int{
				{0, 4, 7},
				{4, 0, 3},
				{7, 3, 0},
			},
			minCities: 2,
			maxCities: 3,
			budget:    5,
			// Explanation:
			// Among two-node subsets, best is connecting nodes 0 and 1 with cost 4 and profit 3.
			// All spanning trees for 3 nodes exceed the budget.
			expected: 3,
		},
		{
			name: "Four cities but not meeting budget for minCities=3",
			N:    4,
			profits: [][]int{
				{0, 10, 10, 10},
				{10, 0, 10, 10},
				{10, 10, 0, 10},
				{10, 10, 10, 0},
			},
			costs: [][]int{
				{0, 10, 10, 10},
				{10, 0, 10, 10},
				{10, 10, 0, 10},
				{10, 10, 10, 0},
			},
			minCities: 3,
			maxCities: 4,
			budget:    5,
			// Explanation:
			// The minimum cost to connect any 3 cities is at least 20 which is over the budget.
			expected: -1,
		},
		{
			name: "Single city network",
			N:    2,
			profits: [][]int{
				{0, 5},
				{5, 0},
			},
			costs: [][]int{
				{0, 100},
				{100, 0},
			},
			minCities: 1,
			maxCities: 1,
			budget:    50,
			// Explanation:
			// Only one city is selected. A single node is considered connected, profit sum is 0.
			expected: 0,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := MaxNetworkProfit(tc.N, tc.profits, tc.minCities, tc.maxCities, tc.budget, tc.costs)
			if result != tc.expected {
				t.Errorf("Test %q: expected %d, got %d", tc.name, tc.expected, result)
			}
		})
	}
}

func TestMaxNetworkProfitEdgeCases(t *testing.T) {
	// Edge case where N = 1 and network is trivial.
	N := 1
	profits := [][]int{
		{0},
	}
	costs := [][]int{
		{0},
	}
	minCities := 1
	maxCities := 1
	budget := 0
	expected := 0

	result := MaxNetworkProfit(N, profits, minCities, maxCities, budget, costs)
	if result != expected {
		t.Errorf("Edge case N=1: expected %d, got %d", expected, result)
	}

	// Edge case where it is impossible due to negative profits but low budget
	N = 2
	profits = [][]int{
		{0, -5},
		{-5, 0},
	}
	costs = [][]int{
		{0, 50},
		{50, 0},
	}
	minCities = 2
	maxCities = 2
	budget = 40
	expected = -1

	result = MaxNetworkProfit(N, profits, minCities, maxCities, budget, costs)
	if result != expected {
		t.Errorf("Edge case negative profit: expected %d, got %d", expected, result)
	}
}

func BenchmarkMaxNetworkProfit(b *testing.B) {
	// Benchmark with a moderate size input.
	N := 10
	profits := make([][]int, N)
	costs := make([][]int, N)
	for i := 0; i < N; i++ {
		profits[i] = make([]int, N)
		costs[i] = make([]int, N)
		for j := 0; j < N; j++ {
			if i == j {
				profits[i][j] = 0
				costs[i][j] = 0
			} else {
				profits[i][j] = (i + j) % 7 // arbitrary profit pattern
				costs[i][j] = (i*j)%5 + 1    // arbitrary cost pattern ensuring positive costs
			}
		}
	}
	minCities := 5
	maxCities := 10
	budget := 50

	b.ResetTimer()
	for n := 0; n < b.N; n++ {
		_ = MaxNetworkProfit(N, profits, minCities, maxCities, budget, costs)
	}
}

// Helper function to compare 2D slices (if needed in future tests)
func equal2DSlices(a, b [][]int) bool {
	return reflect.DeepEqual(a, b)
}