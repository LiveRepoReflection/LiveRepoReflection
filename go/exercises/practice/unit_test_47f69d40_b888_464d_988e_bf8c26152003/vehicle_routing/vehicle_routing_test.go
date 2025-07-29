package vehicle_routing

import (
	"reflect"
	"testing"
)

func TestFindOptimalRoutes(t *testing.T) {
	type testCase struct {
		name          string
		nodes         []string
		edges         []Edge
		vehicles      []Vehicle
		trafficEvents []TrafficEvent
		queryTime     int
		expected      map[string][]string
		wantErr       bool
	}

	testCases := []testCase{
		{
			name:  "Valid input with direct route better at queryTime=7",
			nodes: []string{"A", "B", "C"},
			edges: []Edge{
				{From: "A", To: "B", Weight: 10},
				{From: "B", To: "C", Weight: 15},
				{From: "A", To: "C", Weight: 30},
			},
			vehicles: []Vehicle{
				{ID: "V1", Start: "A", End: "C", DepartureTime: 0},
			},
			trafficEvents: []TrafficEvent{
				{Node: "B", StartTime: 5, EndTime: 15, Delay: 20},
			},
			queryTime: 7,
			// Direct route A->C cost=30 < A->B->C cost=10+20+15=45
			expected: map[string][]string{"V1": {"A", "C"}},
			wantErr:  false,
		},
		{
			name:  "Valid input with indirect route better at queryTime=2",
			nodes: []string{"A", "B", "C"},
			edges: []Edge{
				{From: "A", To: "B", Weight: 10},
				{From: "B", To: "C", Weight: 15},
				{From: "A", To: "C", Weight: 30},
			},
			vehicles: []Vehicle{
				{ID: "V1", Start: "A", End: "C", DepartureTime: 0},
			},
			trafficEvents: []TrafficEvent{
				{Node: "B", StartTime: 5, EndTime: 15, Delay: 20},
			},
			queryTime: 2,
			// At queryTime 2, no traffic delay active, so route A->B->C cost=10+15=25 < direct route 30.
			expected: map[string][]string{"V1": {"A", "B", "C"}},
			wantErr:  false,
		},
		{
			name:  "Overlapping traffic events on node",
			nodes: []string{"A", "B", "C"},
			edges: []Edge{
				{From: "A", To: "B", Weight: 10},
				{From: "B", To: "C", Weight: 15},
				{From: "A", To: "C", Weight: 40}, // increased direct route weight to favor indirect if no delays
			},
			vehicles: []Vehicle{
				{ID: "V1", Start: "A", End: "C", DepartureTime: 0},
			},
			trafficEvents: []TrafficEvent{
				{Node: "B", StartTime: 5, EndTime: 15, Delay: 20},
				{Node: "B", StartTime: 10, EndTime: 20, Delay: 10},
			},
			queryTime: 12,
			// Both events active at B, so delay = 20+10=30, indirect route cost=10+30+15=55, direct route cost=40.
			expected: map[string][]string{"V1": {"A", "C"}},
			wantErr:  false,
		},
		{
			name:  "Invalid node in edges causes error",
			nodes: []string{"A", "B", "C"},
			edges: []Edge{
				{From: "A", To: "D", Weight: 10}, // "D" not in nodes list
				{From: "B", To: "C", Weight: 15},
			},
			vehicles: []Vehicle{
				{ID: "V2", Start: "A", End: "C", DepartureTime: 0},
			},
			trafficEvents: []TrafficEvent{},
			queryTime:     5,
			expected:      nil,
			wantErr:       true,
		},
		{
			name:  "Vehicle duplicate ID causes error",
			nodes: []string{"A", "B", "C"},
			edges: []Edge{
				{From: "A", To: "B", Weight: 5},
				{From: "B", To: "C", Weight: 5},
			},
			vehicles: []Vehicle{
				{ID: "V3", Start: "A", End: "C", DepartureTime: 0},
				{ID: "V3", Start: "A", End: "C", DepartureTime: 0}, // duplicate ID
			},
			trafficEvents: []TrafficEvent{},
			queryTime:     3,
			expected:      nil,
			wantErr:       true,
		},
		{
			name:  "Disconnected graph returns empty route",
			nodes: []string{"A", "B", "C"},
			edges: []Edge{
				{From: "A", To: "B", Weight: 10},
				// No edge connecting to C
			},
			vehicles: []Vehicle{
				{ID: "V4", Start: "A", End: "C", DepartureTime: 0},
			},
			trafficEvents: []TrafficEvent{},
			queryTime:     10,
			// Not reachable, so route should be empty slice
			expected: map[string][]string{"V4": {}},
			wantErr:  false,
		},
		{
			name:          "Empty inputs return empty result without error",
			nodes:         []string{},
			edges:         []Edge{},
			vehicles:      []Vehicle{},
			trafficEvents: []TrafficEvent{},
			queryTime:     0,
			expected:      map[string][]string{},
			wantErr:       false,
		},
		{
			name:  "Vehicle departure time in future still computes route correctly",
			nodes: []string{"A", "B", "C", "D"},
			edges: []Edge{
				{From: "A", To: "B", Weight: 5},
				{From: "B", To: "C", Weight: 5},
				{From: "C", To: "D", Weight: 5},
				{From: "A", To: "D", Weight: 20},
			},
			vehicles: []Vehicle{
				{ID: "V5", Start: "A", End: "D", DepartureTime: 10},
			},
			trafficEvents: []TrafficEvent{
				{Node: "B", StartTime: 12, EndTime: 18, Delay: 5},
			},
			queryTime: 5, // queryTime before departure, but calculation should use vehicle's departure time for route
			// Expected route: A->B->C->D cost = 5 + 5 + 5 = 15 vs direct A->D cost 20,
			// No delay since departure is at 10 and event starts at 12.
			expected: map[string][]string{"V5": {"A", "B", "C", "D"}},
			wantErr:  false,
		},
	}

	for _, tc := range testCases {
		result, err := FindOptimalRoutes(tc.nodes, tc.edges, tc.vehicles, tc.trafficEvents, tc.queryTime)
		if tc.wantErr {
			if err == nil {
				t.Errorf("%s: expected error but got nil", tc.name)
			}
			continue
		} else {
			if err != nil {
				t.Errorf("%s: unexpected error: %v", tc.name, err)
				continue
			}
		}
		// For each vehicle, if the expected route is empty, ensure the key exists
		for vid, route := range tc.expected {
			resRoute, ok := result[vid]
			if !ok {
				t.Errorf("%s: expected vehicle ID %s not present in result", tc.name, vid)
				continue
			}
			if !reflect.DeepEqual(resRoute, route) {
				t.Errorf("%s: for vehicle ID %s, expected route %v, got %v", tc.name, vid, route, resRoute)
			}
		}
		// Also ensure no extra vehicles are present in result when expected map is not empty
		if len(result) != len(tc.expected) {
			t.Errorf("%s: expected result map length %d, got %d", tc.name, len(tc.expected), len(result))
		}
	}
}