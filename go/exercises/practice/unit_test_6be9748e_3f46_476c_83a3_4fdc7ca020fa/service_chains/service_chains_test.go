package service_chains

import (
	"math"
	"testing"
)

type testCase struct {
	name             string
	C                [][]float64
	requiredServices []int
	N                int
	expected         float64
}

func almostEqual(a, b float64) bool {
	const eps = 1e-9
	return math.Abs(a-b) < eps
}

func TestFindMinCost(t *testing.T) {
	testCases := []testCase{
		{
			name: "single_service",
			C: [][]float64{
				{1.5, 2.5, 3.5},
				{0.0, 1.0, 2.0},
				{3.0, 0.5, 0.5},
				{2.0, 2.0, 0.0},
			},
			requiredServices: []int{1},
			N:                3,
			expected:         2.5,
		},
		{
			name: "two_services_ordered",
			C: [][]float64{
				{1.5, 2.5, 3.5},
				{0.0, 1.0, 2.0},
				{3.0, 0.5, 0.5},
				{2.0, 2.0, 0.0},
			},
			requiredServices: []int{0, 1},
			N:                3,
			// Calculation: order [0,1] => C[0][0] + C[0+1][1] = 1.5 + 1.0 = 2.5
			expected: 2.5,
		},
		{
			name: "three_services_full",
			C: [][]float64{
				{1.5, 2.5, 3.5},
				{0.0, 1.0, 2.0},
				{3.0, 0.5, 0.5},
				{2.0, 2.0, 0.0},
			},
			requiredServices: []int{0, 1, 2},
			N:                3,
			// Calculation: best order [0,1,2] => C[0][0] + C[0+1][1] + C[1+1][2] = 1.5 + 1.0 + 0.5 = 3.0
			expected: 3.0,
		},
		{
			name: "invalid_required",
			C: [][]float64{
				{1.5, 2.5, 3.5},
				{0.0, 1.0, 2.0},
				{3.0, 0.5, 0.5},
				{2.0, 2.0, 0.0},
			},
			requiredServices: []int{0, 3}, // 3 is out of range since valid indices are 0..2
			N:                3,
			expected:         -1.0,
		},
		{
			name:             "empty_required",
			C: [][]float64{
				{1.5, 2.5, 3.5},
				{0.0, 1.0, 2.0},
				{3.0, 0.5, 0.5},
				{2.0, 2.0, 0.0},
			},
			requiredServices: []int{},
			N:                3,
			// When no required services, the total cost can be considered 0.
			expected: 0.0,
		},
		{
			name: "four_services_subset",
			C: [][]float64{
				{1.0, 2.0, 3.0, 4.0},
				{1.0, 1.0, 2.0, 3.0},
				{2.0, 3.0, 1.0, 1.0},
				{3.0, 2.0, 4.0, 1.0},
				{1.0, 5.0, 2.0, 2.0},
			},
			requiredServices: []int{1, 3},
			N:                4,
			// Two orders:
			// [1,3]: C[0][1] + C[1+1][3] = 2.0 + 1.0 = 3.0
			// [3,1]: C[0][3] + C[3+1][1] = 4.0 + 5.0 = 9.0
			// Minimum = 3.0
			expected: 3.0,
		},
		{
			name: "four_services_three_req",
			C: [][]float64{
				{1.0, 2.0, 3.0, 4.0},
				{1.0, 1.0, 2.0, 3.0},
				{2.0, 3.0, 1.0, 1.0},
				{3.0, 2.0, 4.0, 1.0},
				{1.0, 5.0, 2.0, 2.0},
			},
			requiredServices: []int{0, 2, 3},
			N:                4,
			// Evaluate orders:
			// [0,2,3]: C[0][0] + C[0+1][2] + C[2+1][3] = 1.0 + 2.0 + 1.0 = 4.0
			// Other orders yield higher costs.
			expected: 4.0,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := FindMinCost(tc.C, tc.requiredServices, tc.N)
			if !almostEqual(result, tc.expected) {
				t.Errorf("Test %q failed: expected %v, got %v", tc.name, tc.expected, result)
			}
		})
	}
}