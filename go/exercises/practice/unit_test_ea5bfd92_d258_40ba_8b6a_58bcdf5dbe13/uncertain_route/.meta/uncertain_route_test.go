package uncertain_route

import (
	"reflect"
	"testing"
)

// TestSimpleRoute tests a basic route from A to C via B.
func TestSimpleRoute(t *testing.T) {
	g := NewGraph()
	// Graph:
	// A -> B: travelTime = 10, uncertainty = 0.1 (risk = 1)
	// B -> C: travelTime = 15, uncertainty = 0.2 (risk = 3)
	// Total risk-adjusted travel time = 10 + 15 + 1 + 3 = 29
	g.AddEdge("A", "B", 5, 10, 0.1)
	g.AddEdge("B", "C", 7, 15, 0.2)

	route, err := g.PlanRoute("A", "C")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	expected := []string{"A", "B", "C"}
	if !reflect.DeepEqual(route, expected) {
		t.Errorf("Expected route %v, got %v", expected, route)
	}
}

// TestNoRoute tests that the system returns an error when no valid route exists.
func TestNoRoute(t *testing.T) {
	g := NewGraph()
	g.AddEdge("A", "B", 5, 10, 0.1)
	// There is no route from A to D.
	route, err := g.PlanRoute("A", "D")
	if err == nil {
		t.Errorf("Expected error for no route, but got route %v", route)
	}
}

// TestDynamicUpdate tests dynamic updates of edge properties affecting optimal route.
func TestDynamicUpdate(t *testing.T) {
	g := NewGraph()
	// Initial Graph:
	// A -> B: travelTime = 10, uncertainty = 0.1 (risk = 1)
	// B -> D: travelTime = 20, uncertainty = 0.2 (risk = 4)
	// Total for A->B->D = 10 + 20 + 1 + 4 = 35
	// A -> C: travelTime = 15, uncertainty = 0.2 (risk = 3)
	// C -> D: travelTime = 10, uncertainty = 0.1 (risk = 1)
	// Total for A->C->D = 15 + 10 + 3 + 1 = 29 (optimal initially)
	g.AddEdge("A", "B", 5, 10, 0.1)
	g.AddEdge("B", "D", 6, 20, 0.2)
	g.AddEdge("A", "C", 4, 15, 0.2)
	g.AddEdge("C", "D", 3, 10, 0.1)

	// Verify that the initial optimal route is A -> C -> D.
	route, err := g.PlanRoute("A", "D")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	expected := []string{"A", "C", "D"}
	if !reflect.DeepEqual(route, expected) {
		t.Errorf("Expected route %v, got %v", expected, route)
	}

	// Update edge A->C increasing travelTime to 25 (risk becomes 25 * 0.2 = 5).
	g.UpdateEdge("A", "C", 4, 25, 0.2)
	// Now:
	// A -> C: 25 + 5 = 30 combined, C -> D: 10 + 1 = 11, total = 41
	// A -> B->D remains at 35, making it the new optimal route.
	route, err = g.PlanRoute("A", "D")
	if err != nil {
		t.Fatalf("Unexpected error after update: %v", err)
	}
	expected = []string{"A", "B", "D"}
	if !reflect.DeepEqual(route, expected) {
		t.Errorf("After update, expected route %v, got %v", expected, route)
	}
}

// TestMultipleValidPaths tests that among several valid paths, the one with the minimum risk-adjusted travel time is chosen.
func TestMultipleValidPaths(t *testing.T) {
	g := NewGraph()
	// Graph with multiple paths from A to D:
	// Path 1: A -> B -> D
	//   A->B: travelTime = 5, uncertainty = 0.1 (risk = 0.5)
	//   B->D: travelTime = 15, uncertainty = 0.2 (risk = 3)
	//   Total = 5 + 15 + 0.5 + 3 = 23.5
	// Path 2: A -> C -> D
	//   A->C: travelTime = 7, uncertainty ≈ 0.142857 (risk ≈ 1)
	//   C->D: travelTime = 10, uncertainty = 0.15 (risk = 1.5)
	//   Total = 7 + 10 + 1 + 1.5 = 19.5  (optimal)
	// Path 3: A -> E -> D
	//   A->E: travelTime = 6, uncertainty = 0.1 (risk = 0.6)
	//   E->D: travelTime = 12, uncertainty = 0.2 (risk = 2.4)
	//   Total = 6 + 12 + 0.6 + 2.4 = 21
	g.AddEdge("A", "B", 3, 5, 0.1)
	g.AddEdge("B", "D", 4, 15, 0.2)
	g.AddEdge("A", "C", 2, 7, 0.142857)
	g.AddEdge("C", "D", 3, 10, 0.15)
	g.AddEdge("A", "E", 2.5, 6, 0.1)
	g.AddEdge("E", "D", 3, 12, 0.2)

	route, err := g.PlanRoute("A", "D")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	// The optimal route should be A -> C -> D.
	expected := []string{"A", "C", "D"}
	if !reflect.DeepEqual(route, expected) {
		t.Errorf("Expected route %v, got %v", expected, route)
	}
}