package traffic_scheduler

import (
	"reflect"
	"testing"
)

// Dummy allowedRoads function for test case 1.
// For intersection 0: state 0 allows movement on road (0,1)
// For intersection 1: state 1 allows movement on road (1,0)
func allowedRoadsCase1(intersection, state int, roads [][2]int) map[[2]int]bool {
	result := make(map[[2]int]bool)
	if intersection == 0 && state == 0 {
		result[[2]int{0, 1}] = true
	}
	if intersection == 1 && state == 1 {
		result[[2]int{1, 0}] = true
	}
	return result
}

// Dummy allowedRoads function for test case 2 (3 intersections).
// For simplicity, we define the following behavior:
// For each intersection, if state equals 0 then allow the first adjacent road (if exists),
// if state equals 1 then allow the second adjacent road (if exists),
// if state equals 2 then allow all adjacent roads.
func allowedRoadsCase2Factory(roadsMap map[int][][2]int) func(int, int) map[[2]int]bool {
	return func(intersection, state int) map[[2]int]bool {
		result := make(map[[2]int]bool)
		adjacent, exists := roadsMap[intersection]
		if !exists {
			return result
		}
		switch state {
		case 0:
			if len(adjacent) >= 1 {
				result[adjacent[0]] = true
			}
		case 1:
			if len(adjacent) >= 2 {
				result[adjacent[1]] = true
			}
		case 2:
			for _, road := range adjacent {
				result[road] = true
			}
		default:
			// For states >= 3, return empty set.
		}
		return result
	}
}

// Test that the ScheduleTrafficLights function returns a schedule that has the correct dimensions
// and valid state values.
func TestScheduleTrafficLights(t *testing.T) {
	tests := []struct {
		name         string
		n            int
		m            int
		roads        [][2]int
		k            int
		d            [][]int
		h            int
		tCost        int
		allowedRoads func(int, int) map[[2]int]bool
	}{
		{
			name:  "Two intersections simple case",
			n:     2,
			m:     1,
			roads: [][2]int{{0, 1}},
			k:     2,
			d: [][]int{
				{0, 5},
				{3, 0},
			},
			h:     4,
			tCost: 1,
			allowedRoads: func(intersection, state int) map[[2]int]bool {
				return allowedRoadsCase1(intersection, state, [][2]int{{0, 1}})
			},
		},
		{
			name:  "Three intersections moderate case",
			n:     3,
			m:     3,
			roads: [][2]int{{0, 1}, {1, 2}, {0, 2}},
			k:     3,
			d: [][]int{
				{0, 4, 2},
				{3, 0, 5},
				{1, 2, 0},
			},
			h:     5,
			tCost: 1,
			allowedRoads: func(intersection, state int) map[[2]int]bool {
				// Create a map of adjacent roads for each intersection based on the provided roads.
				roadsMap := make(map[int][][2]int)
				for _, road := range [][2]int{{0, 1}, {1, 2}, {0, 2}} {
					roadsMap[road[0]] = append(roadsMap[road[0]], road)
					// Since roads are bidirectional add the reverse as well.
					roadsMap[road[1]] = append(roadsMap[road[1]], [2]int{road[1], road[0]})
				}
				// Use allowedRoadsCase2Factory to generate allowed roads.
				factory := allowedRoadsCase2Factory(roadsMap)
				return factory(intersection, state)
			},
		},
		{
			name:  "No traffic demand case",
			n:     2,
			m:     1,
			roads: [][2]int{{0, 1}},
			k:     2,
			d: [][]int{
				{0, 0},
				{0, 0},
			},
			h:     3,
			tCost: 1,
			allowedRoads: func(intersection, state int) map[[2]int]bool {
				// Simply allow road movement on state 0 at any intersection.
				result := make(map[[2]int]bool)
				if state == 0 {
					if intersection == 0 {
						result[[2]int{0, 1}] = true
					}
					if intersection == 1 {
						result[[2]int{1, 0}] = true
					}
				}
				return result
			},
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			// Assume ScheduleTrafficLights is available in the package.
			schedule := ScheduleTrafficLights(tc.n, tc.m, tc.roads, tc.k, tc.allowedRoads, tc.d, tc.h, tc.tCost)
			// Check the schedule dimensions.
			if len(schedule) != tc.n {
				t.Fatalf("expected schedule outer length %d, got %d", tc.n, len(schedule))
			}
			for i := 0; i < tc.n; i++ {
				if len(schedule[i]) != tc.h {
					t.Fatalf("expected schedule[%d] length %d, got %d", i, tc.h, len(schedule[i]))
				}
				// Check that each traffic light state is within the valid range [0, k-1].
				for j := 0; j < tc.h; j++ {
					state := schedule[i][j]
					if state < 0 || state >= tc.k {
						t.Fatalf("invalid state %d at schedule[%d][%d], expected in range [0,%d)", state, i, j, tc.k)
					}
				}
			}
		})
	}
}

// Benchmark for the ScheduleTrafficLights function.
func BenchmarkScheduleTrafficLights(b *testing.B) {
	// Use a moderate size test case for benchmarking.
	n := 3
	m := 3
	roads := [][2]int{{0, 1}, {1, 2}, {0, 2}}
	k := 3
	d := [][]int{
		{0, 4, 2},
		{3, 0, 5},
		{1, 2, 0},
	}
	h := 5
	tCost := 1

	// Create the allowedRoads function as in test case 2.
	roadsMap := make(map[int][][2]int)
	for _, road := range roads {
		roadsMap[road[0]] = append(roadsMap[road[0]], road)
		roadsMap[road[1]] = append(roadsMap[road[1]], [2]int{road[1], road[0]})
	}
	allowedRoads := allowedRoadsCase2Factory(roadsMap)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		schedule := ScheduleTrafficLights(n, m, roads, k, allowedRoads, d, h, tCost)
		// Ensure the generated schedule has the correct dimensions (performance cost negligible).
		if !reflect.DeepEqual(len(schedule), n) {
			b.Fatalf("unexpected schedule dimensions")
		}
	}
}