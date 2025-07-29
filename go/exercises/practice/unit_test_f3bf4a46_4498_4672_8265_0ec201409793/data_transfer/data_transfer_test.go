package data_transfer

import (
	"testing"
)

type testCase struct {
	description    string
	n              int
	m              int
	capacities     []int
	cost           []int
	availability   [][]bool
	k              int
	datacenterIDs  []int
	dataItemIDs    []int
	sizes          []int
	expectedResult int
}

func TestMinimizeDataTransferCost(t *testing.T) {
	testCases := []testCase{
		{
			description: "No Transfer Needed",
			n:           2,
			m:           2,
			capacities:  []int{100, 100},
			cost:        []int{10, 20},
			availability: [][]bool{
				{true, true},
				{true, true},
			},
			k:              2,
			datacenterIDs:  []int{0, 1},
			dataItemIDs:    []int{1, 0},
			sizes:          []int{10, 20}, // sizes for item0 and item1
			expectedResult: 0,
		},
		{
			description: "Single Transfer Required",
			n:           2,
			m:           2,
			capacities:  []int{100, 100},
			cost:        []int{5, 15},
			availability: [][]bool{
				{true, false},
				{false, true},
			},
			k:              1,
			datacenterIDs:  []int{1},
			dataItemIDs:    []int{0},
			sizes:          []int{10, 20},
			// Transfer from DC0 to DC1: cost = size[0] * cost[DC0] = 10 * 5 = 50
			expectedResult: 50,
		},
		{
			description: "Multiple Requests, Single Transfer",
			n:           2,
			m:           2,
			capacities:  []int{100, 100},
			cost:        []int{5, 15},
			availability: [][]bool{
				{true, false},
				{false, true},
			},
			k:              2,
			datacenterIDs:  []int{1, 1},
			dataItemIDs:    []int{0, 0},
			sizes:          []int{10, 20},
			// Only one transfer is needed for DC1 to get item0 from DC0 at cost 10*5 = 50.
			expectedResult: 50,
		},
		{
			description: "Capacity Constraint Scenario",
			n:           3,
			m:           3,
			capacities:  []int{1000, 50, 150},
			cost:        []int{8, 3, 5},
			availability: [][]bool{
				{true, true, false},
				{false, false, true},
				{false, false, false},
			},
			k:             3,
			datacenterIDs: []int{2, 2, 1},
			dataItemIDs:   []int{0, 2, 1},
			sizes:         []int{20, 40, 30}, // sizes for items 0, 1, 2 respectively
			// Request details:
			// DC2 requests item0 -> only available at DC0: cost = 20*8 = 160
			// DC2 requests item2 -> only available at DC1: cost = 30*3 = 90
			// DC1 requests item1 -> only available at DC0: cost = 40*8 = 320
			// Total = 160+90+320 = 570
			expectedResult: 570,
		},
		{
			description: "Complex Scenario with Alternative Sources",
			n:           3,
			m:           2,
			capacities:  []int{200, 200, 200},
			cost:        []int{10, 5, 8},
			availability: [][]bool{
				{true, false},
				{false, true},
				{true, true},
			},
			k:             3,
			datacenterIDs: []int{1, 0, 1},
			dataItemIDs:   []int{0, 1, 0},
			sizes:         []int{30, 50},
			// Request details:
			// For DC1 requesting item0: available from DC0 (cost 10) and DC2 (cost 8). Cheaper is DC2: cost = 30*8 = 240.
			// For DC0 requesting item1: available from DC1 (cost 5) and DC2 (cost 8). Cheaper is DC1: cost = 50*5 = 250.
			// Duplicate request for DC1 item0 incurred no extra cost.
			// Total = 240+250 = 490.
			expectedResult: 490,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			actual := MinimizeDataTransferCost(tc.n, tc.m, tc.capacities, tc.cost, tc.availability, tc.k, tc.datacenterIDs, tc.dataItemIDs, tc.sizes)
			if actual != tc.expectedResult {
				t.Errorf("For test case '%s', expected cost %d but got %d", tc.description, tc.expectedResult, actual)
			}
		})
	}
}

func BenchmarkMinimizeDataTransferCost(b *testing.B) {
	// Use a representative complex test case for benchmarking.
	n := 3
	m := 3
	capacities := []int{1000, 1000, 1000}
	cost := []int{8, 3, 5}
	availability := [][]bool{
		{true, true, false},
		{false, false, true},
		{true, false, false},
	}
	k := 5
	datacenterIDs := []int{2, 1, 0, 2, 1}
	dataItemIDs := []int{0, 2, 1, 2, 0}
	sizes := []int{20, 40, 30}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinimizeDataTransferCost(n, m, capacities, cost, availability, k, datacenterIDs, dataItemIDs, sizes)
	}
}