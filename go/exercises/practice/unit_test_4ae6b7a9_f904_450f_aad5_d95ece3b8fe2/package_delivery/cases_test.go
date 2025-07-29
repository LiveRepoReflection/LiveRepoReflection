package packagedelivery

// TestCase represents a single test scenario
type TestCase struct {
	Description string
	Hubs        []Hub
	Routes      []Route
	Packages    []Package
	Expected    int
}

// Hub represents a delivery hub in the network
type Hub struct {
	ID             int
	Capacity       int
	ProcessingCost int
}

// Route represents a transportation route between two hubs
type Route struct {
	SourceHubID      int
	DestinationHubID int
	CostPerPackage   int
}

// Package represents a package to be delivered
type Package struct {
	ID                int
	SourceHubID       int
	DestinationHubID  int
}

var testCases = []TestCase{
	// Basic test case with two hubs and two packages
	{
		Description: "Basic case with two hubs",
		Hubs: []Hub{
			{ID: 1, Capacity: 10, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 1},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 2},
			{ID: 2, SourceHubID: 1, DestinationHubID: 2},
		},
		Expected: 14,
	},
	// Test case with a package already at its destination
	{
		Description: "Package already at destination",
		Hubs: []Hub{
			{ID: 1, Capacity: 10, ProcessingCost: 2},
			{ID: 2, Capacity: 10, ProcessingCost: 3},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 1},
		},
		Expected: 2, // Only processing cost at the hub
	},
	// Test case with multiple possible routes
	{
		Description: "Multiple possible routes",
		Hubs: []Hub{
			{ID: 1, Capacity: 10, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 2},
			{ID: 3, Capacity: 10, ProcessingCost: 3},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
			{SourceHubID: 1, DestinationHubID: 3, CostPerPackage: 2},
			{SourceHubID: 3, DestinationHubID: 2, CostPerPackage: 1},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 2},
		},
		Expected: 7, // 1->3->2 route (2+1) + processing (1+3+2)
	},
	// Test case with capacity constraints
	{
		Description: "Capacity constraints",
		Hubs: []Hub{
			{ID: 1, Capacity: 1, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 1},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 2},
			{ID: 2, SourceHubID: 1, DestinationHubID: 2},
		},
		Expected: -1, // Impossible due to hub 1 capacity
	},
	// Test case with a more complex network
	{
		Description: "Complex network",
		Hubs: []Hub{
			{ID: 1, Capacity: 10, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 2},
			{ID: 3, Capacity: 10, ProcessingCost: 1},
			{ID: 4, Capacity: 10, ProcessingCost: 3},
			{ID: 5, Capacity: 10, ProcessingCost: 2},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 10},
			{SourceHubID: 1, DestinationHubID: 3, CostPerPackage: 5},
			{SourceHubID: 2, DestinationHubID: 4, CostPerPackage: 6},
			{SourceHubID: 2, DestinationHubID: 5, CostPerPackage: 4},
			{SourceHubID: 3, DestinationHubID: 2, CostPerPackage: 3},
			{SourceHubID: 3, DestinationHubID: 5, CostPerPackage: 8},
			{SourceHubID: 4, DestinationHubID: 5, CostPerPackage: 2},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 5},
			{ID: 2, SourceHubID: 3, DestinationHubID: 4},
		},
		Expected: 29, // Package 1: 1->3->2->5 (5+3+4) + (1+1+2+2), Package 2: 3->2->4 (3+6) + (1+2+3)
	},
	// Test case with disconnected graph
	{
		Description: "Disconnected graph",
		Hubs: []Hub{
			{ID: 1, Capacity: 10, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 2},
			{ID: 3, Capacity: 10, ProcessingCost: 3},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 3},
		},
		Expected: -1, // No route to destination
	},
	// Test case with a hub of zero capacity
	{
		Description: "Hub with zero capacity",
		Hubs: []Hub{
			{ID: 1, Capacity: 0, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 2},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 2},
		},
		Expected: -1, // Impossible due to hub 1 having zero capacity
	},
	// Test case with circular routes
	{
		Description: "Circular routes",
		Hubs: []Hub{
			{ID: 1, Capacity: 10, ProcessingCost: 1},
			{ID: 2, Capacity: 10, ProcessingCost: 2},
			{ID: 3, Capacity: 10, ProcessingCost: 3},
		},
		Routes: []Route{
			{SourceHubID: 1, DestinationHubID: 2, CostPerPackage: 5},
			{SourceHubID: 2, DestinationHubID: 3, CostPerPackage: 5},
			{SourceHubID: 3, DestinationHubID: 1, CostPerPackage: 5},
		},
		Packages: []Package{
			{ID: 1, SourceHubID: 1, DestinationHubID: 3},
		},
		Expected: 16, // 1->2->3 (5+5) + (1+2+3)
	},
}