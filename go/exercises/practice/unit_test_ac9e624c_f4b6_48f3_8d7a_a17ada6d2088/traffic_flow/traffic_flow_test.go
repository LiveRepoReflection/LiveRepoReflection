package traffic_flow

import (
	"reflect"
	"testing"
)

// Test cases assume the existence of the following types and function in the production code:
// type Road struct {
//     To         int
//     Capacity   int
//     TravelTime int
// }
// type Route struct {
//     Path  []int
//     Count int
// }
// type Phase struct{}
// OptimizeTrafficLights(graph map[int][]Road, routes []Route, phases [][]Phase, totalCycle int, congestionFactor float64, simulationTime int) [][]int

func sum(slice []int) int {
	total := 0
	for _, x := range slice {
		total += x
	}
	return total
}

func TestOptimizeTrafficLights(t *testing.T) {
	tests := []struct {
		description      string
		graph            map[int][]Road
		routes           []Route
		phases           [][]Phase
		totalCycle       int
		congestionFactor float64
		simulationTime   int
	}{
		{
			description: "simple two-intersection network",
			graph: map[int][]Road{
				0: {
					{To: 1, Capacity: 2, TravelTime: 5},
				},
				1: {},
			},
			routes: []Route{
				{Path: []int{0, 1}, Count: 10},
			},
			// Both intersections have 2 phases.
			phases: [][]Phase{
				{{}, {}},
				{{}, {}},
			},
			totalCycle:       60,
			congestionFactor: 0.5,
			simulationTime:   100,
		},
		{
			description: "three-intersection complex network",
			graph: map[int][]Road{
				0: {
					{To: 1, Capacity: 3, TravelTime: 4},
					{To: 2, Capacity: 2, TravelTime: 6},
				},
				1: {
					{To: 2, Capacity: 4, TravelTime: 3},
				},
				2: {},
			},
			routes: []Route{
				{Path: []int{0, 1, 2}, Count: 20},
				{Path: []int{0, 2}, Count: 5},
			},
			// All intersections have 3 phases.
			phases: [][]Phase{
				{{}, {}, {}},
				{{}, {}, {}},
				{{}, {}, {}},
			},
			totalCycle:       60,
			congestionFactor: 0.5,
			simulationTime:   120,
		},
	}

	for _, tc := range tests {
		t.Run(tc.description, func(t *testing.T) {
			result := OptimizeTrafficLights(tc.graph, tc.routes, tc.phases, tc.totalCycle, tc.congestionFactor, tc.simulationTime)
			// Check number of intersections in result matches the number of intersections in phases.
			if len(result) != len(tc.phases) {
				t.Fatalf("expected result length %d, got %d", len(tc.phases), len(result))
			}
			// For each intersection, check that the number of phase durations equals the number of provided phases and they sum to totalCycle.
			for i, durations := range result {
				if len(durations) != len(tc.phases[i]) {
					t.Errorf("intersection %d: expected %d phase durations, got %d", i, len(tc.phases[i]), len(durations))
				}
				total := sum(durations)
				if total != tc.totalCycle {
					t.Errorf("intersection %d: expected total cycle %d, got %d", i, tc.totalCycle, total)
				}
				for j, d := range durations {
					if d < 0 {
						t.Errorf("intersection %d, phase %d: duration is negative (%d)", i, j, d)
					}
				}
			}
		})
	}
}

func TestOptimizeTrafficLights_Consistency(t *testing.T) {
	// This test verifies that repeated runs with the same input produce consistent output structure.
	graph := map[int][]Road{
		0: {
			{To: 1, Capacity: 2, TravelTime: 5},
		},
		1: {},
	}
	routes := []Route{
		{Path: []int{0, 1}, Count: 15},
	}
	phases := [][]Phase{
		{{}, {}},
		{{}, {}},
	}
	totalCycle := 60
	congestionFactor := 0.5
	simulationTime := 100

	res1 := OptimizeTrafficLights(graph, routes, phases, totalCycle, congestionFactor, simulationTime)
	res2 := OptimizeTrafficLights(graph, routes, phases, totalCycle, congestionFactor, simulationTime)

	// Compare the structure of the two results.
	if len(res1) != len(res2) {
		t.Fatalf("inconsistent number of intersections: %d vs %d", len(res1), len(res2))
	}
	for i := range res1 {
		if len(res1[i]) != len(res2[i]) {
			t.Fatalf("inconsistent number of phases at intersection %d: %d vs %d", i, len(res1[i]), len(res2[i]))
		}
	}
	// Although the solution could be optimization based and may have randomness,
	// this test only checks for consistency of structure.
	if !reflect.DeepEqual(len(res1[0]), len(res2[0])) {
		t.Errorf("inconsistent phase durations structure")
	}
}

func BenchmarkOptimizeTrafficLights(b *testing.B) {
	graph := map[int][]Road{
		0: {
			{To: 1, Capacity: 2, TravelTime: 5},
			{To: 2, Capacity: 3, TravelTime: 4},
		},
		1: {
			{To: 2, Capacity: 4, TravelTime: 3},
		},
		2: {},
	}
	routes := []Route{
		{Path: []int{0, 1, 2}, Count: 50},
		{Path: []int{0, 2}, Count: 30},
	}
	phases := [][]Phase{
		{{}, {}, {}},
		{{}, {}, {}},
		{{}, {}, {}},
	}
	totalCycle := 60
	congestionFactor := 0.5
	simulationTime := 150

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = OptimizeTrafficLights(graph, routes, phases, totalCycle, congestionFactor, simulationTime)
	}
}