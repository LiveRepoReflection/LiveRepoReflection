package traffic_optimizer

import (
	"testing"
)

// isValidRoute checks if the provided route is contiguous in the given graph.
func isValidRoute(graph map[int][]RoadSegment, route []int) bool {
	if len(route) < 2 {
		return false
	}
	// Build an adjacency map for quick lookup.
	adj := make(map[int]map[int]bool)
	for node, segments := range graph {
		adj[node] = make(map[int]bool)
		for _, seg := range segments {
			adj[node][seg.ToNode] = true
		}
	}
	// Verify that each consecutive pair in the route is connected.
	for i := 0; i < len(route)-1; i++ {
		from, to := route[i], route[i+1]
		if !adj[from][to] {
			return false
		}
	}
	return true
}

func TestOptimizeTrafficFlow_SimpleGraph(t *testing.T) {
	// Create a simple graph
	graph := map[int][]RoadSegment{
		1: {
			{ToNode: 2, BaseTravelTime: 10, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
			{ToNode: 3, BaseTravelTime: 15, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		2: {
			{ToNode: 3, BaseTravelTime: 10, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
			{ToNode: 4, BaseTravelTime: 20, Capacity: 50, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		3: {
			{ToNode: 4, BaseTravelTime: 10, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		4: {},
	}

	// Create vehicle routes
	vehicleRoutes := []VehicleRoute{
		{StartNode: 1, EndNode: 4},
		{StartNode: 2, EndNode: 4},
		{StartNode: 1, EndNode: 3},
	}

	iterations := 50

	optimizedRoutes, avgCommuteTime := OptimizeTrafficFlow(graph, vehicleRoutes, iterations)
	if len(optimizedRoutes) != len(vehicleRoutes) {
		t.Errorf("Expected %d vehicle routes, got %d", len(vehicleRoutes), len(optimizedRoutes))
	}

	// Validate each route is continuous and begins and ends with the correct nodes.
	for idx, route := range optimizedRoutes {
		if len(route.Path) < 2 {
			t.Errorf("Route %d is too short: %v", idx, route.Path)
		}
		if route.Path[0] != route.StartNode || route.Path[len(route.Path)-1] != route.EndNode {
			t.Errorf("Route %d does not start/end correctly: got %v, expected start %d and end %d",
				idx, route.Path, route.StartNode, route.EndNode)
		}
		if !isValidRoute(graph, route.Path) {
			t.Errorf("Route %d is not a valid path in the graph: %v", idx, route.Path)
		}
	}

	if avgCommuteTime <= 0 {
		t.Errorf("Expected positive average commute time, got %f", avgCommuteTime)
	}
}

func TestOptimizeTrafficFlow_DisconnectedGraph(t *testing.T) {
	// Create a graph with disconnected components.
	graph := map[int][]RoadSegment{
		1: {
			{ToNode: 2, BaseTravelTime: 10, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		2: {},
		3: {
			{ToNode: 4, BaseTravelTime: 10, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		4: {},
	}

	vehicleRoutes := []VehicleRoute{
		{StartNode: 1, EndNode: 2},
		// This route is disconnected (no path from 1 to 4 in the graph).
		{StartNode: 1, EndNode: 4},
	}

	iterations := 20

	optimizedRoutes, avgCommuteTime := OptimizeTrafficFlow(graph, vehicleRoutes, iterations)

	// For the disconnected route, expect an empty path.
	for _, route := range optimizedRoutes {
		if route.StartNode == 1 && route.EndNode == 4 {
			if len(route.Path) != 0 {
				t.Errorf("Expected empty path for disconnected route from %d to %d, got %v",
					route.StartNode, route.EndNode, route.Path)
			}
		} else {
			if len(route.Path) == 0 {
				t.Errorf("Expected valid path for route from %d to %d, got empty path",
					route.StartNode, route.EndNode)
			}
		}
	}

	if avgCommuteTime < 0 {
		t.Errorf("Average commute time should not be negative, got %f", avgCommuteTime)
	}
}

func TestOptimizeTrafficFlow_CongestionEffect(t *testing.T) {
	// Create a graph where congestion significantly influences travel time.
	graph := map[int][]RoadSegment{
		1: {
			{ToNode: 2, BaseTravelTime: 5, Capacity: 10, CongestionFactor: 0.5, TrafficVolume: 0},
			{ToNode: 3, BaseTravelTime: 10, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		2: {
			{ToNode: 4, BaseTravelTime: 5, Capacity: 10, CongestionFactor: 0.5, TrafficVolume: 0},
		},
		3: {
			{ToNode: 4, BaseTravelTime: 5, Capacity: 100, CongestionFactor: 0.1, TrafficVolume: 0},
		},
		4: {},
	}

	vehicleRoutes := []VehicleRoute{
		{StartNode: 1, EndNode: 4},
		{StartNode: 1, EndNode: 4},
		{StartNode: 1, EndNode: 4},
		{StartNode: 1, EndNode: 4},
	}

	iterations := 30

	optimizedRoutes, avgCommuteTime := OptimizeTrafficFlow(graph, vehicleRoutes, iterations)

	// Validate that every route from 1 to 4 is continuous.
	for idx, route := range optimizedRoutes {
		if route.Path[0] != 1 || route.Path[len(route.Path)-1] != 4 {
			t.Errorf("Route %d does not start at 1 and end at 4: %v", idx, route.Path)
		}
		if !isValidRoute(graph, route.Path) {
			t.Errorf("Route %d is not valid in the graph: %v", idx, route.Path)
		}
	}

	if avgCommuteTime <= 0 {
		t.Errorf("Expected positive average commute time, got %f", avgCommuteTime)
	}
}