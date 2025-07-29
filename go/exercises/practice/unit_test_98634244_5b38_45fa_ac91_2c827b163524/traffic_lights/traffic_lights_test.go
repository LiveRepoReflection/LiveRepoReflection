package traffic_lights

import (
	"reflect"
	"testing"
)

type testCase struct {
	name       string
	N          int
	M          int
	restricted [][]int
	expected   int
}

func TestMinTrafficLights(t *testing.T) {
	testCases := []testCase{
		{
			name:       "single_intersection_no_roads",
			N:          1,
			M:          1,
			restricted: [][]int{},
			expected:   0,
		},
		{
			name:       "one_row_two_columns",
			N:          1,
			M:          2,
			restricted: [][]int{},
			expected:   1,
		},
		{
			name:       "two_by_two_with_restriction",
			N:          2,
			M:          2,
			restricted: [][]int{{0, 0}},
			expected:   2,
		},
		{
			name:       "two_by_three_with_restriction",
			N:          2,
			M:          3,
			restricted: [][]int{{0, 1}},
			expected:   3,
		},
		{
			name:       "three_by_three_with_center_restricted",
			N:          3,
			M:          3,
			restricted: [][]int{{1, 1}},
			expected:   4,
		},
		{
			name:       "four_by_four_no_restrictions",
			N:          4,
			M:          4,
			restricted: [][]int{},
			expected:   8,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			res := MinTrafficLights(tc.N, tc.M, tc.restricted)
			if res != tc.expected {
				t.Fatalf("MinTrafficLights(%d, %d, %v) = %d; expected %d",
					tc.N, tc.M, tc.restricted, res, tc.expected)
			}
		})
	}
}

func BenchmarkMinTrafficLights(b *testing.B) {
	testCases := []testCase{
		{
			name:       "four_by_four_no_restrictions",
			N:          4,
			M:          4,
			restricted: [][]int{},
			expected:   8,
		},
		{
			name:       "three_by_three_with_center_restricted",
			N:          3,
			M:          3,
			restricted: [][]int{{1, 1}},
			expected:   4,
		},
		{
			name:       "two_by_three_with_restriction",
			N:          2,
			M:          3,
			restricted: [][]int{{0, 1}},
			expected:   3,
		},
	}

	for _, tc := range testCases {
		b.Run(tc.name, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				res := MinTrafficLights(tc.N, tc.M, tc.restricted)
				if !reflect.DeepEqual(res, tc.expected) {
					b.Fatalf("MinTrafficLights(%d, %d, %v) = %d; expected %d",
						tc.N, tc.M, tc.restricted, res, tc.expected)
				}
			}
		})
	}
}