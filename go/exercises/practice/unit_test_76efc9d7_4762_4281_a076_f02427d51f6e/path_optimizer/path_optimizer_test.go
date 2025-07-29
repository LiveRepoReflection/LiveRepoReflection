package path_optimizer

import (
	"testing"
)

func TestOptimizeRoutes_FulfilledRequests(t *testing.T) {
	// Setup timeline for edges
	edgeTimelineFast := []TimeWeight{
		{timestamp: 1000, weight: 10},
		{timestamp: 2000, weight: 15},
	}
	edgeTimelineSlow := []TimeWeight{
		{timestamp: 1000, weight: 20},
		{timestamp: 2000, weight: 30},
	}

	// Create graph: A->B and A->C; B->C
	graph := map[string][]Edge{
		"A": {
			{to: "B", weightTimeline: edgeTimelineFast},
			{to: "C", weightTimeline: edgeTimelineSlow},
		},
		"B": {
			{to: "C", weightTimeline: edgeTimelineFast},
		},
		"C": {},
	}

	// Request from A to C starting at 1500 with deadline 1600
	req1 := Request{from: "A", to: "C", startTime: 1500, deadline: 1600}
	// Request from A to B starting at 1500 with deadline 1540
	req2 := Request{from: "A", to: "B", startTime: 1500, deadline: 1540}

	requests := []Request{req1, req2}

	assignments := OptimizeRoutes(graph, requests)
	// Expect both requests to be fulfilled
	if len(assignments) != 2 {
		t.Fatalf("expected 2 assignments, got %d", len(assignments))
	}

	// Validate each assignment
	for _, a := range assignments {
		// Check start and end nodes in path
		if a.path[0] != a.request.from || a.path[len(a.path)-1] != a.request.to {
			t.Errorf("invalid path for request %v: path=%v", a.request, a.path)
		}
		// Check time constraints
		if a.startTime < a.request.startTime {
			t.Errorf("assignment start time %d is before request start time %d", a.startTime, a.request.startTime)
		}
		if a.arrivalTime > a.request.deadline {
			t.Errorf("assignment arrival time %d exceeds request deadline %d", a.arrivalTime, a.request.deadline)
		}
		// Check path validity: consecutive nodes should be connected by an edge in the graph
		for i := 0; i < len(a.path)-1; i++ {
			if !edgeExists(graph, a.path[i], a.path[i+1]) {
				t.Errorf("invalid path between %s and %s", a.path[i], a.path[i+1])
			}
		}
	}
}

func TestOptimizeRoutes_NoPath(t *testing.T) {
	// Create a graph where destination is unreachable
	edgeTimeline := []TimeWeight{
		{timestamp: 1000, weight: 10},
	}
	graph := map[string][]Edge{
		"A": {
			{to: "B", weightTimeline: edgeTimeline},
		},
		"B": {}, // No edge from B to C
		"C": {},
	}
	req := Request{from: "A", to: "C", startTime: 1100, deadline: 1200}
	assignments := OptimizeRoutes(graph, []Request{req})
	// Expect no assignments because no valid path exists.
	if len(assignments) != 0 {
		t.Fatalf("expected 0 assignments, got %d", len(assignments))
	}
}

func TestOptimizeRoutes_EdgeImpassable(t *testing.T) {
	// Create a graph where edge is impassable at request start time
	edgeTimeline := []TimeWeight{
		{timestamp: 2000, weight: 10}, // Edge becomes passable only at or after 2000
	}
	graph := map[string][]Edge{
		"A": {
			{to: "B", weightTimeline: edgeTimeline},
		},
		"B": {
			{to: "C", weightTimeline: []TimeWeight{
				{timestamp: 2000, weight: 10},
			}},
		},
		"C": {},
	}
	req := Request{from: "A", to: "C", startTime: 1500, deadline: 2500}
	assignments := OptimizeRoutes(graph, []Request{req})
	// Expect no assignment because the edge from A to B is impassable at startTime 1500.
	if len(assignments) != 0 {
		t.Fatalf("expected 0 assignments for impassable edge, got %d", len(assignments))
	}
}

func TestOptimizeRoutes_MultiplePaths(t *testing.T) {
	// Graph with two possible routes from A to C: A->B->C and A->D->C
	edgeTimelineStandard := []TimeWeight{
		{timestamp: 1000, weight: 10},
	}
	edgeTimelineQuick := []TimeWeight{
		{timestamp: 1000, weight: 5},
	}

	graph := map[string][]Edge{
		"A": {
			{to: "B", weightTimeline: edgeTimelineStandard},
			{to: "D", weightTimeline: edgeTimelineQuick},
		},
		"B": {
			{to: "C", weightTimeline: edgeTimelineStandard},
		},
		"D": {
			{to: "C", weightTimeline: []TimeWeight{
				{timestamp: 1000, weight: 5},
			}},
		},
		"C": {},
	}

	req := Request{from: "A", to: "C", startTime: 1100, deadline: 1300}
	assignments := OptimizeRoutes(graph, []Request{req})
	// Expect one assignment fulfilling the request
	if len(assignments) != 1 {
		t.Fatalf("expected 1 assignment, got %d", len(assignments))
	}
	assignment := assignments[0]
	// Check that route is valid and optimal according to minimal travel time
	if len(assignment.path) != 3 {
		t.Errorf("expected path length of 3 nodes, got %v", assignment.path)
	}
	// Intermediate node must be either B or D and should be connected from A
	if assignment.path[1] != "B" && assignment.path[1] != "D" {
		t.Errorf("unexpected intermediate node: %s", assignment.path[1])
	}
	// Validate consecutive edge connectivity in the path
	for i := 0; i < len(assignment.path)-1; i++ {
		if !edgeExists(graph, assignment.path[i], assignment.path[i+1]) {
			t.Errorf("invalid path segment from %s to %s", assignment.path[i], assignment.path[i+1])
		}
	}
}

func edgeExists(graph map[string][]Edge, from, to string) bool {
	edges, exists := graph[from]
	if !exists {
		return false
	}
	for _, edge := range edges {
		if edge.to == to {
			return true
		}
	}
	return false
}