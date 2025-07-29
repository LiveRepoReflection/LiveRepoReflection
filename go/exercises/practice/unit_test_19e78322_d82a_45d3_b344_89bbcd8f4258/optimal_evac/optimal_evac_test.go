package optimal_evac

import (
	"math"
	"testing"
)

func floatEquals(a, b float64) bool {
	const eps = 1e-6
	return math.Abs(a-b) < eps
}

func TestOptimalEvacuationTime(t *testing.T) {
	testCases := []struct {
		description         string
		n                   int
		edges               [][]int // Each inner slice: [u, v, weight]
		population          []int
		evacuationCenters   []int
		maxRoadCapacity     int
		expectedEvacTime    float64
	}{
		{
			description:       "Basic chain graph with single evacuation center",
			n:                 4,
			edges:             [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}},
			population:        []int{100, 0, 0, 0},
			evacuationCenters: []int{3},
			maxRoadCapacity:   200,
			expectedEvacTime:  3.0,
		},
		{
			description:       "Unreachable node causes evacuation failure",
			n:                 3,
			edges:             [][]int{{0, 1, 1}},
			population:        []int{10, 20, 30},
			evacuationCenters: []int{0},
			maxRoadCapacity:   100,
			expectedEvacTime:  -1,
		},
		{
			description:       "Chain graph with two evacuation centers",
			n:                 5,
			edges:             [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}, {3, 4, 1}},
			population:        []int{100, 200, 300, 200, 100},
			evacuationCenters: []int{0, 4},
			maxRoadCapacity:   1000,
			expectedEvacTime:  2.0,
		},
		{
			description:       "Capacity constraint exceeded",
			n:                 2,
			edges:             [][]int{{0, 1, 2}},
			population:        []int{0, 6000},
			evacuationCenters: []int{0},
			maxRoadCapacity:   5000,
			expectedEvacTime:  -1,
		},
		{
			description: "Complex graph with cycles and multiple paths",
			n:           6,
			edges: [][]int{
				{0, 1, 2},
				{0, 2, 5},
				{1, 2, 1},
				{1, 3, 2},
				{2, 3, 2},
				{3, 4, 1},
				{4, 5, 1},
				{2, 5, 5},
			},
			population:        []int{50, 100, 100, 50, 200, 150},
			evacuationCenters: []int{0, 5},
			maxRoadCapacity:   300,
			expectedEvacTime:  3.0,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Call the function defined in the optimal_evac package.
			result := OptimalEvacuationTime(tc.n, tc.edges, tc.population, tc.evacuationCenters, tc.maxRoadCapacity)
			if !floatEquals(result, tc.expectedEvacTime) {
				t.Fatalf("Test failed: %s\nExpected evacuation time: %v, got: %v", tc.description, tc.expectedEvacTime, result)
			}
		})
	}
}