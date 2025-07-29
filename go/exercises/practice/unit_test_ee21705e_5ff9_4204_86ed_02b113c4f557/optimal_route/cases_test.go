package optimalroute

import (
	"math"
)

// TestCase represents a single test case for the optimal route planner
type TestCase struct {
	description     string
	graphEdges      [][4]int // [source, destination, travel_time, toll_cost]
	truckRoutes     []TruckRoute
	maxTravelTime   int
	timeTollWeight  float64
	expectedResults []ExpectedResult
}

// TruckRoute represents a truck's assigned route
type TruckRoute struct {
	truckID        int
	startDepot     int
	deliveryPoints []int
}

// ExpectedResult represents the expected output for a truck's route
type ExpectedResult struct {
	truckID    int
	route      []int
	totalCost  float64
	incomplete bool
}

// getTestCases returns all test cases for the optimal route planner
func getTestCases() []TestCase {
	return []TestCase{
		{
			description: "Single truck with one delivery location - example from question",
			graphEdges: [][4]int{
				{1, 2, 10, 2},
				{1, 3, 15, 1},
				{2, 4, 20, 3},
				{3, 4, 5, 1},
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{4}},
			},
			maxTravelTime:  40,
			timeTollWeight: 0.5,
			expectedResults: []ExpectedResult{
				{101, []int{1, 3, 4}, 21.0, false},
			},
		},
		{
			description: "Single truck with multiple delivery locations",
			graphEdges: [][4]int{
				{1, 2, 10, 2},
				{1, 3, 15, 1},
				{2, 3, 5, 1},
				{2, 4, 20, 3},
				{3, 4, 5, 1},
				{3, 5, 10, 2},
				{4, 5, 15, 0},
				{4, 6, 10, 2},
				{5, 6, 5, 1},
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{3, 5, 6}},
			},
			maxTravelTime:  100,
			timeTollWeight: 0.5,
			expectedResults: []ExpectedResult{
				{101, []int{1, 3, 3, 5, 5, 6}, 35.5, false},
			},
		},
		{
			description: "Multiple trucks with different routes",
			graphEdges: [][4]int{
				{1, 2, 10, 2},
				{1, 3, 15, 1},
				{2, 3, 5, 1},
				{2, 4, 20, 3},
				{3, 4, 5, 1},
				{3, 5, 10, 2},
				{4, 5, 15, 0},
				{4, 6, 10, 2},
				{5, 6, 5, 1},
				{5, 7, 20, 4},
				{6, 7, 15, 2},
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{3, 5, 6}},
				{102, 2, []int{4, 7}},
				{103, 3, []int{6}},
			},
			maxTravelTime:  100,
			timeTollWeight: 0.5,
			expectedResults: []ExpectedResult{
				{101, []int{1, 3, 3, 5, 5, 6}, 35.5, false},
				{102, []int{2, 4, 4, 6, 6, 7}, 55.0, false},
				{103, []int{3, 5, 5, 6}, 16.5, false},
			},
		},
		{
			description: "Truck exceeding maximum travel time",
			graphEdges: [][4]int{
				{1, 2, 10, 2},
				{1, 3, 15, 1},
				{2, 4, 20, 3},
				{3, 4, 5, 1},
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{4}},
			},
			maxTravelTime:  15, // Too short for any possible route
			timeTollWeight: 0.5,
			expectedResults: []ExpectedResult{
				{101, nil, math.Inf(1), true}, // Incomplete route
			},
		},
		{
			description: "Different weight factors affecting route choice",
			graphEdges: [][4]int{
				{1, 2, 10, 5},  // Fast but expensive
				{1, 3, 20, 1},  // Slow but cheap
				{2, 4, 15, 10}, // Fast but expensive
				{3, 4, 30, 2},  // Slow but cheap
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{4}}, // Time-prioritizing truck
				{102, 1, []int{4}}, // Cost-prioritizing truck
			},
			maxTravelTime:  100,
			timeTollWeight: 0.1, // For truck 101 (prioritizes time)
			expectedResults: []ExpectedResult{
				{101, []int{1, 2, 2, 4}, 27.5, false}, // Faster route with higher toll
				{102, []int{1, 3, 3, 4}, 50.3, false}, // Slower route with lower toll (using different weight in the test)
			},
		},
		{
			description: "Large circular graph with multiple possible paths",
			graphEdges: [][4]int{
				{1, 2, 10, 2}, {1, 3, 15, 1}, {1, 4, 25, 0},
				{2, 3, 5, 1}, {2, 5, 15, 3},
				{3, 4, 10, 2}, {3, 5, 20, 1}, {3, 6, 30, 0},
				{4, 7, 15, 2},
				{5, 6, 10, 1}, {5, 8, 20, 2},
				{6, 7, 5, 1}, {6, 9, 15, 3},
				{7, 8, 10, 0}, {7, 10, 20, 2},
				{8, 9, 5, 1}, {8, 10, 15, 0},
				{9, 10, 10, 2},
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{6, 10}},
				{102, 2, []int{8}},
				{103, 5, []int{7, 9}},
			},
			maxTravelTime:  200,
			timeTollWeight: 0.5,
			expectedResults: []ExpectedResult{
				{101, []int{1, 3, 3, 6, 6, 7, 7, 10}, 77.0, false},
				{102, []int{2, 5, 5, 8}, 36.5, false},
				{103, []int{5, 6, 6, 7, 7, 8, 8, 9}, 37.0, false},
			},
		},
		{
			description: "Edge case: No solution exists for one truck",
			graphEdges: [][4]int{
				{1, 2, 10, 2},
				{1, 3, 15, 1},
				{2, 4, 20, 3},
				{3, 4, 5, 1},
				// No paths to node 5
			},
			truckRoutes: []TruckRoute{
				{101, 1, []int{4}},  // Can reach destination
				{102, 1, []int{5}},  // Cannot reach destination
				{103, 2, []int{4}},  // Can reach destination
			},
			maxTravelTime:  100,
			timeTollWeight: 0.5,
			expectedResults: []ExpectedResult{
				{101, []int{1, 3, 3, 4}, 21.0, false},
				{102, nil, math.Inf(1), true}, // Incomplete route due to unreachable destination
				{103, []int{2, 2, 4}, 21.5, false},
			},
		},
	}
}