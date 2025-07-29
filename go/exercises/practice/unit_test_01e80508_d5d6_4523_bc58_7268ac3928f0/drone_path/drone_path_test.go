package drone_path

import (
	"reflect"
	"testing"
)

// Assume these types and the FindOptimalPath function are defined in drone_path.go
// type Node struct {
// 	ID   int
// 	X, Y float64
// 	Risk int
// }
//
// type Edge struct {
// 	From        int
// 	To          int
// 	FlightTime  float64
// 	MaxAltitude float64
// }
//
// type Graph struct {
// 	Nodes map[int]Node
// 	Edges map[int][]Edge
// }
//
// type NoFlyZone struct {
// 	CenterX, CenterY float64
// 	Radius           float64
// }
//
// // FindOptimalPath finds the optimal path (slice of node IDs) from start to end
// // given the constraints. It returns an error if no valid path exists.
// func FindOptimalPath(g Graph, start, end int, maxRisk int, maxTime float64, noFlyZones []NoFlyZone) ([]int, error)

func TestFindOptimalPath(t *testing.T) {
	tests := []struct {
		name         string
		graph        Graph
		start        int
		end          int
		maxRisk      int
		maxTime      float64
		noFlyZones   []NoFlyZone
		expectedPath []int
		expectErr    bool
	}{
		{
			name: "simple_path",
			graph: Graph{
				Nodes: map[int]Node{
					1: {ID: 1, X: 0, Y: 0, Risk: 1},
					2: {ID: 2, X: 1, Y: 0, Risk: 2},
					3: {ID: 3, X: 2, Y: 0, Risk: 1},
				},
				Edges: map[int][]Edge{
					1: {
						{From: 1, To: 2, FlightTime: 1.0, MaxAltitude: 100},
					},
					2: {
						{From: 2, To: 3, FlightTime: 1.0, MaxAltitude: 100},
					},
				},
			},
			start:        1,
			end:          3,
			maxRisk:      5,
			maxTime:      3.0,
			noFlyZones:   []NoFlyZone{},
			expectedPath: []int{1, 2, 3},
			expectErr:    false,
		},
		{
			name: "risk_exceeded",
			graph: Graph{
				Nodes: map[int]Node{
					1: {ID: 1, X: 0, Y: 0, Risk: 1},
					2: {ID: 2, X: 1, Y: 0, Risk: 2},
					3: {ID: 3, X: 2, Y: 0, Risk: 1},
				},
				Edges: map[int][]Edge{
					1: {
						{From: 1, To: 2, FlightTime: 1.0, MaxAltitude: 100},
					},
					2: {
						{From: 2, To: 3, FlightTime: 1.0, MaxAltitude: 100},
					},
				},
			},
			start:        1,
			end:          3,
			maxRisk:      3, // Total risk on path would be 1+2+1 = 4, exceeding limit.
			maxTime:      3.0,
			noFlyZones:   []NoFlyZone{},
			expectedPath: nil,
			expectErr:    true,
		},
		{
			name: "battery_life_exceeded",
			graph: Graph{
				Nodes: map[int]Node{
					1: {ID: 1, X: 0, Y: 0, Risk: 1},
					2: {ID: 2, X: 1, Y: 0, Risk: 2},
					3: {ID: 3, X: 2, Y: 0, Risk: 1},
				},
				Edges: map[int][]Edge{
					1: {
						{From: 1, To: 2, FlightTime: 1.0, MaxAltitude: 100},
					},
					2: {
						{From: 2, To: 3, FlightTime: 1.0, MaxAltitude: 100},
					},
				},
			},
			start:        1,
			end:          3,
			maxRisk:      5,
			maxTime:      1.5, // Total flight time required is 2.0, exceeds battery life.
			noFlyZones:   []NoFlyZone{},
			expectedPath: nil,
			expectErr:    true,
		},
		{
			name: "no_fly_zone_intersection",
			graph: Graph{
				Nodes: map[int]Node{
					1: {ID: 1, X: 0, Y: 0, Risk: 1},
					2: {ID: 2, X: 1, Y: 0, Risk: 1},
					3: {ID: 3, X: 0.2, Y: 1, Risk: 1},
				},
				Edges: map[int][]Edge{
					1: {
						// Direct edge from 1 to 2 that will intersect the no-fly zone
						{From: 1, To: 2, FlightTime: 1.0, MaxAltitude: 100},
						// Alternative edge via node 3 that avoids the no-fly zone
						{From: 1, To: 3, FlightTime: 1.5, MaxAltitude: 100},
					},
					3: {
						{From: 3, To: 2, FlightTime: 1.0, MaxAltitude: 100},
					},
				},
			},
			start:   1,
			end:     2,
			maxRisk: 10,
			maxTime: 3.0,
			noFlyZones: []NoFlyZone{
				{CenterX: 0.5, CenterY: 0, Radius: 0.3},
			},
			// Expected to choose path [1,3,2] because direct path 1->2 intersects the no-fly zone.
			expectedPath: []int{1, 3, 2},
			expectErr:    false,
		},
		{
			name: "choose_valid_tradeoff",
			graph: Graph{
				Nodes: map[int]Node{
					1: {ID: 1, X: 0, Y: 0, Risk: 1},
					2: {ID: 2, X: 1, Y: 0, Risk: 5},
					3: {ID: 3, X: 2, Y: 0, Risk: 1},
					4: {ID: 4, X: 0, Y: 1, Risk: 1},
				},
				Edges: map[int][]Edge{
					1: {
						{From: 1, To: 2, FlightTime: 1.0, MaxAltitude: 100},
						{From: 1, To: 4, FlightTime: 1.2, MaxAltitude: 100},
					},
					2: {
						{From: 2, To: 3, FlightTime: 1.0, MaxAltitude: 100},
					},
					4: {
						{From: 4, To: 3, FlightTime: 1.2, MaxAltitude: 100},
					},
				},
			},
			start:        1,
			end:          3,
			maxRisk:      5,   // Path 1->2->3 risk: 1+5+1 = 7 (invalid)
			maxTime:      3.0, // Both paths under maxTime, but only alternate path meets risk constraints.
			noFlyZones:   []NoFlyZone{},
			expectedPath: []int{1, 4, 3},
			expectErr:    false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			path, err := FindOptimalPath(tc.graph, tc.start, tc.end, tc.maxRisk, tc.maxTime, tc.noFlyZones)
			if tc.expectErr {
				if err == nil {
					t.Errorf("Test case %q expected an error but got none", tc.name)
				}
			} else {
				if err != nil {
					t.Errorf("Test case %q did not expect an error but got: %v", tc.name, err)
					return
				}
				if !reflect.DeepEqual(path, tc.expectedPath) {
					t.Errorf("Test case %q expected path %v, got %v", tc.name, tc.expectedPath, path)
				}
			}
		})
	}
}