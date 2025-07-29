package route_planner

import (
	"strings"
	"testing"
)

func graphsEqual(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i, v := range a {
		if b[i] != v {
			return false
		}
	}
	return true
}

func initGraph(t *testing.T) {
	graphData := "5 7\n" +
		"0 1 5\n" +
		"0 2 10\n" +
		"1 2 3\n" +
		"1 3 15\n" +
		"2 3 1\n" +
		"3 4 2\n" +
		"2 4 20"
	// Clear any previous state by reinitializing the graph.
	// Assume Initialize resets the internal state.
	Initialize(graphData)
}

func TestRoutePlanner(t *testing.T) {
	// Initialize graph before tests.
	initGraph(t)

	t.Run("OptimalRouteWithinDeadline", func(t *testing.T) {
		// Using the initial graph:
		// Route from 0 -> 4: optimal is [0,1,2,3,4] with cost 5+3+1+2 = 11.
		route, totalTime, penaltyFee, err := FindOptimalRoute(0, 4, 20, 1.0)
		if err != nil {
			t.Fatalf("Expected a valid route, got error: %v", err)
		}

		expectedRoute := []int{0, 1, 2, 3, 4}
		if !graphsEqual(route, expectedRoute) {
			t.Fatalf("Expected route %v, got %v", expectedRoute, route)
		}
		if totalTime != 11 {
			t.Fatalf("Expected total time 11, got %d", totalTime)
		}
		if penaltyFee != 0 {
			t.Fatalf("Expected penalty fee 0, got %f", penaltyFee)
		}
	})

	t.Run("DeadlineExceeded", func(t *testing.T) {
		// Deadline less than optimal route time.
		_, _, _, err := FindOptimalRoute(0, 4, 10, 0.5)
		if err == nil {
			t.Fatalf("Expected error due to deadline constraint, got nil")
		}
	})

	t.Run("UpdateEdgeWeightAffectsRoute", func(t *testing.T) {
		// Update the weight of edge 0->1 to a higher value, making route 0->2->3->4 optimal.
		// Current weight for 0->1 is 5, update to 100.
		UpdateEdgeWeight(0, 1, 100)
		// Re-run route finding with generous deadline.
		route, totalTime, penaltyFee, err := FindOptimalRoute(0, 4, 20, 2.0)
		if err != nil {
			t.Fatalf("Expected valid route after update, got error: %v", err)
		}
		// The new optimal route should be [0,2,3,4] with cost 10+1+2 = 13.
		expectedRoute := []int{0, 2, 3, 4}
		if !graphsEqual(route, expectedRoute) {
			t.Fatalf("After update, expected route %v, got %v", expectedRoute, route)
		}
		if totalTime != 13 {
			t.Fatalf("After update, expected total time 13, got %d", totalTime)
		}
		// Even if the route is within deadline, penalty can be recalculated.
		if penaltyFee != 0 {
			t.Fatalf("After update and valid deadline, expected penalty fee 0, got %f", penaltyFee)
		}
		// Reset the edge weight for subsequent tests.
		UpdateEdgeWeight(0, 1, 5)
	})

	t.Run("StartEqualsEnd", func(t *testing.T) {
		// When start and destination are the same.
		route, totalTime, penaltyFee, err := FindOptimalRoute(2, 2, 5, 1.0)
		if err != nil {
			t.Fatalf("Expected valid route for same start and end, got error: %v", err)
		}
		expectedRoute := []int{2}
		if !graphsEqual(route, expectedRoute) {
			t.Fatalf("Expected route %v, got %v", expectedRoute, route)
		}
		if totalTime != 0 {
			t.Fatalf("Expected total time 0 for same start and end, got %d", totalTime)
		}
		if penaltyFee != 0 {
			t.Fatalf("Expected penalty fee 0 for same start and end, got %f", penaltyFee)
		}
	})

	t.Run("NonConnectedNodes", func(t *testing.T) {
		// Test route in a graph where destination is unreachable.
		// In the initial graph, node 4 can reach no node backwards.
		// Testing from node 4 to node 0 should be unreachable.
		_, _, _, err := FindOptimalRoute(4, 0, 100, 1.0)
		if err == nil {
			t.Fatalf("Expected error for unreachable route, got nil")
		}
	})

	t.Run("GraphDataParsing", func(t *testing.T) {
		// Test that additional whitespace or newlines do not affect initialization.
		graphData := strings.Join([]string{
			"5 7",
			"0 1 5",
			"0 2 10",
			"1 2 3",
			"1 3 15",
			"2 3 1",
			"3 4 2",
			"2 4 20",
		}, "\n")
		Initialize(graphData)
		route, totalTime, penaltyFee, err := FindOptimalRoute(0, 4, 20, 1.0)
		if err != nil {
			t.Fatalf("Expected valid route with well-formed graph data, got error: %v", err)
		}
		expectedRoute := []int{0, 1, 2, 3, 4}
		if !graphsEqual(route, expectedRoute) {
			t.Fatalf("Expected route %v, got %v", expectedRoute, route)
		}
		if totalTime != 11 {
			t.Fatalf("Expected total time 11, got %d", totalTime)
		}
		if penaltyFee != 0 {
			t.Fatalf("Expected penalty fee 0, got %f", penaltyFee)
		}
	})
}