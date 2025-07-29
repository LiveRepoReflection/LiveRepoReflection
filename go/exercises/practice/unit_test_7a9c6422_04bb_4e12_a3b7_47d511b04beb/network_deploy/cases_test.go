package network_deploy

import (
	"testing"
)

type testCase struct {
	name     string
	N        int
	M        int
	R        []int
	C        []int
	B        [][]int
	V        [][]int
	S        int
	L        int
	Lxy      [][]int
	K        int
	expected int
}

func TestOptimizeDeployment(t *testing.T) {
	testCases := []testCase{
		{
			name:     "single service",
			N:        1,
			M:        0,
			R:        []int{3},
			C:        []int{100},
			B:        [][]int{{0}},
			V:        [][]int{{0}},
			S:        5,
			L:        10,
			Lxy:      [][]int{{0}},
			K:        1,
			expected: 100,
		},
		{
			name: "two services forced same server by bandwidth",
			N:    2,
			M:    1,
			R:    []int{3, 3},
			C:    []int{200, 300},
			B: [][]int{
				{0, 0},
				{0, 0},
			},
			V: [][]int{
				{0, 50},
				{50, 0},
			},
			S:        10,
			L:        10,
			Lxy:      [][]int{{0, 5}, {5, 0}},
			K:        1,
			expected: 500,
		},
		{
			name: "impossible due to redundancy constraint",
			N:    3,
			M:    3,
			R:    []int{2, 2, 2},
			C:    []int{100, 150, 200},
			B: [][]int{
				{0, 100, 100},
				{100, 0, 100},
				{100, 100, 0},
			},
			V: [][]int{
				{0, 30, 30},
				{30, 0, 30},
				{30, 30, 0},
			},
			S:        5,
			L:        10,
			Lxy:      [][]int{{0, 3}, {3, 0}},
			K:        2,
			expected: -1,
		},
		{
			name: "latency constraint forces same server",
			N:    2,
			M:    1,
			R:    []int{4, 3},
			C:    []int{150, 200},
			B: [][]int{
				{0, 100},
				{100, 0},
			},
			V: [][]int{
				{0, 50},
				{50, 0},
			},
			S:        10,
			L:        5,
			Lxy:      [][]int{{0, 10}, {10, 0}},
			K:        1,
			expected: 350,
		},
		{
			name: "four services with mixed constraints",
			N:    4,
			M:    6,
			R:    []int{3, 3, 4, 2},
			C:    []int{100, 200, 150, 50},
			B: [][]int{
				{0, 100, 100, 0},
				{100, 0, 100, 100},
				{100, 100, 0, 100},
				{0, 100, 100, 0},
			},
			V: [][]int{
				{0, 30, 30, 0},
				{30, 0, 30, 30},
				{30, 30, 0, 30},
				{0, 30, 30, 0},
			},
			S:        10,
			L:        8,
			Lxy:      [][]int{{0, 5}, {5, 0}},
			K:        1,
			expected: 500,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := OptimizeDeployment(tc.N, tc.M, tc.R, tc.C, tc.B, tc.V, tc.S, tc.L, tc.Lxy, tc.K)
			if result != tc.expected {
				t.Errorf("Test case '%s' failed: expected %d, got %d", tc.name, tc.expected, result)
			}
		})
	}
}