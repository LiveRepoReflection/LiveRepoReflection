package traffic_router

import (
	"math"
	"testing"
)

func TestRouteVehicle(t *testing.T) {
	// Test graph setup
	edges := []Edge{
		{From: 0, To: 1, Capacity: 100, BaseTime: 10},
		{From: 0, To: 2, Capacity: 50, BaseTime: 5},
		{From: 1, To: 3, Capacity: 80, BaseTime: 15},
		{From: 2, To: 3, Capacity: 40, BaseTime: 20},
		{From: 1, To: 2, Capacity: 30, BaseTime: 8},
	}

	tests := []struct {
		name        string
		request     VehicleRequest
		wantError   bool
		validRoute  bool
		maxPathLen  int
		minPathLen  int
	}{
		{
			name: "Basic path test",
			request: VehicleRequest{
				Origin:      0,
				Destination: 3,
				Priority:    5,
			},
			wantError:  false,
			validRoute: true,
			maxPathLen: 4,
			minPathLen: 2,
		},
		{
			name: "High priority vehicle",
			request: VehicleRequest{
				Origin:      0,
				Destination: 3,
				Priority:    10,
			},
			wantError:  false,
			validRoute: true,
			maxPathLen: 4,
			minPathLen: 2,
		},
		{
			name: "Invalid origin",
			request: VehicleRequest{
				Origin:      10,
				Destination: 3,
				Priority:    5,
			},
			wantError:  true,
			validRoute: false,
		},
		{
			name: "Invalid destination",
			request: VehicleRequest{
				Origin:      0,
				Destination: 10,
				Priority:    5,
			},
			wantError:  true,
			validRoute: false,
		},
		{
			name: "Invalid priority",
			request: VehicleRequest{
				Origin:      0,
				Destination: 3,
				Priority:    11,
			},
			wantError:  true,
			validRoute: false,
		},
	}

	router := NewTrafficRouter(4, edges) // 4 nodes in the graph

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			route, err := router.RouteVehicle(tt.request)

			// Check error cases
			if tt.wantError {
				if err == nil {
					t.Errorf("Expected error but got none")
				}
				return
			}

			if err != nil {
				t.Errorf("Unexpected error: %v", err)
				return
			}

			// Validate route
			if tt.validRoute {
				if len(route) == 0 {
					t.Error("Expected non-empty route but got empty route")
					return
				}

				if len(route) > tt.maxPathLen {
					t.Errorf("Route too long: got %v nodes, want at most %v", len(route), tt.maxPathLen)
				}

				if len(route) < tt.minPathLen {
					t.Errorf("Route too short: got %v nodes, want at least %v", len(route), tt.minPathLen)
				}

				// Check if route starts at origin and ends at destination
				if route[0] != tt.request.Origin {
					t.Errorf("Route doesn't start at origin: got %v, want %v", route[0], tt.request.Origin)
				}

				if route[len(route)-1] != tt.request.Destination {
					t.Errorf("Route doesn't end at destination: got %v, want %v", route[len(route)-1], tt.request.Destination)
				}

				// Verify route continuity
				for i := 0; i < len(route)-1; i++ {
					if !hasEdge(edges, route[i], route[i+1]) {
						t.Errorf("Invalid route segment: no edge between %v and %v", route[i], route[i+1])
					}
				}
			}
		})
	}
}

func TestConcurrentRequests(t *testing.T) {
	edges := []Edge{
		{From: 0, To: 1, Capacity: 100, BaseTime: 10},
		{From: 1, To: 2, Capacity: 100, BaseTime: 10},
		{From: 0, To: 2, Capacity: 50, BaseTime: 15},
	}

	router := NewTrafficRouter(3, edges)
	requestCount := 100

	// Create a channel to collect results
	results := make(chan struct {
		route []int
		err   error
	}, requestCount)

	// Send multiple concurrent requests
	for i := 0; i < requestCount; i++ {
		go func() {
			route, err := router.RouteVehicle(VehicleRequest{
				Origin:      0,
				Destination: 2,
				Priority:    5,
			})
			results <- struct {
				route []int
				err   error
			}{route, err}
		}()
	}

	// Collect and validate results
	for i := 0; i < requestCount; i++ {
		result := <-results
		if result.err != nil {
			t.Errorf("Request %d failed: %v", i, result.err)
			continue
		}

		if len(result.route) == 0 {
			t.Errorf("Request %d returned empty route", i)
			continue
		}

		if result.route[0] != 0 || result.route[len(result.route)-1] != 2 {
			t.Errorf("Request %d returned invalid route: %v", i, result.route)
		}
	}
}

func TestTrafficCongestion(t *testing.T) {
	edges := []Edge{
		{From: 0, To: 1, Capacity: 10, BaseTime: 10},
		{From: 0, To: 2, Capacity: 20, BaseTime: 15},
		{From: 1, To: 3, Capacity: 15, BaseTime: 10},
		{From: 2, To: 3, Capacity: 15, BaseTime: 10},
	}

	router := NewTrafficRouter(4, edges)

	// Send multiple requests to create congestion
	var routes [][]int
	for i := 0; i < 20; i++ {
		route, err := router.RouteVehicle(VehicleRequest{
			Origin:      0,
			Destination: 3,
			Priority:    5,
		})
		if err != nil {
			t.Fatalf("Unexpected error: %v", err)
		}
		routes = append(routes, route)
	}

	// Verify that routes are distributed across different paths
	path1Count := 0 // Count of routes going through node 1
	path2Count := 0 // Count of routes going through node 2

	for _, route := range routes {
		if containsNode(route, 1) {
			path1Count++
		}
		if containsNode(route, 2) {
			path2Count++
		}
	}

	// Verify that traffic is somewhat balanced between paths
	if path1Count == 0 || path2Count == 0 {
		t.Error("Expected traffic to be distributed across multiple paths")
	}
}

func TestPriorityRouting(t *testing.T) {
	edges := []Edge{
		{From: 0, To: 1, Capacity: 10, BaseTime: 10},
		{From: 0, To: 2, Capacity: 5, BaseTime: 5},
		{From: 1, To: 3, Capacity: 10, BaseTime: 10},
		{From: 2, To: 3, Capacity: 5, BaseTime: 5},
	}

	router := NewTrafficRouter(4, edges)

	// Create congestion with low-priority vehicles
	for i := 0; i < 10; i++ {
		router.RouteVehicle(VehicleRequest{
			Origin:      0,
			Destination: 3,
			Priority:    1,
		})
	}

	// Route a high-priority vehicle
	highPriorityRoute, err := router.RouteVehicle(VehicleRequest{
		Origin:      0,
		Destination: 3,
		Priority:    10,
	})

	if err != nil {
		t.Fatalf("Unexpected error routing high-priority vehicle: %v", err)
	}

	// Calculate the theoretical travel time for the high-priority route
	travelTime := calculateRouteTime(highPriorityRoute, edges, router)

	// Route a low-priority vehicle
	lowPriorityRoute, err := router.RouteVehicle(VehicleRequest{
		Origin:      0,
		Destination: 3,
		Priority:    1,
	})

	if err != nil {
		t.Fatalf("Unexpected error routing low-priority vehicle: %v", err)
	}

	lowPriorityTime := calculateRouteTime(lowPriorityRoute, edges, router)

	// Verify that high-priority vehicle gets a faster route
	if travelTime > lowPriorityTime {
		t.Errorf("High-priority route (%v) should be faster than low-priority route (%v)",
			travelTime, lowPriorityTime)
	}
}

// Helper functions

func hasEdge(edges []Edge, from, to int) bool {
	for _, edge := range edges {
		if edge.From == from && edge.To == to {
			return true
		}
	}
	return false
}

func containsNode(route []int, node int) bool {
	for _, n := range route {
		if n == node {
			return true
		}
	}
	return false
}

func calculateRouteTime(route []int, edges []Edge, router *TrafficRouter) float64 {
	var totalTime float64
	for i := 0; i < len(route)-1; i++ {
		for _, edge := range edges {
			if edge.From == route[i] && edge.To == route[i+1] {
				flow := router.GetCurrentFlow(edge.From, edge.To)
				actualTime := float64(edge.BaseTime) * (1 + math.Pow(float64(flow)/float64(edge.Capacity), 2))
				totalTime += actualTime
				break
			}
		}
	}
	return totalTime
}
