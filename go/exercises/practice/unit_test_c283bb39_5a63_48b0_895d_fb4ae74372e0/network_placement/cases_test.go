package networkplacement

// Test cases for the network placement problem
var testCases = []struct {
	description     string
	nodes           int
	edges           []Edge
	demand          [][]int
	routersCount    int
	routerCapacity  int
	reductionFactor float64
	expected        []int
}{
	{
		description:     "Linear Network with 4 nodes, place 1 router",
		nodes:           4,
		edges:           []Edge{{0, 1, 10}, {1, 2, 10}, {2, 3, 10}},
		demand:          [][]int{{0, 0, 0, 100}, {0, 0, 0, 0}, {0, 0, 0, 0}, {100, 0, 0, 0}},
		routersCount:    1,
		routerCapacity:  1000,
		reductionFactor: 0.5,
		expected:        []int{1}, // Optimal placement should be at node 1 or 2
	},
	{
		description:     "Star Network with 5 nodes, place 1 router",
		nodes:           5,
		edges:           []Edge{{0, 1, 10}, {0, 2, 15}, {0, 3, 20}, {0, 4, 25}},
		demand:          [][]int{{0, 10, 10, 10, 10}, {10, 0, 5, 5, 5}, {10, 5, 0, 5, 5}, {10, 5, 5, 0, 5}, {10, 5, 5, 5, 0}},
		routersCount:    1,
		routerCapacity:  1000,
		reductionFactor: 0.5,
		expected:        []int{0}, // Center of the star
	},
	{
		description:     "Ring Network with 6 nodes, place 2 routers",
		nodes:           6,
		edges:           []Edge{{0, 1, 10}, {1, 2, 10}, {2, 3, 10}, {3, 4, 10}, {4, 5, 10}, {5, 0, 10}},
		demand:          [][]int{{0, 5, 15, 20, 15, 5}, {5, 0, 5, 15, 20, 15}, {15, 5, 0, 5, 15, 20}, {20, 15, 5, 0, 5, 15}, {15, 20, 15, 5, 0, 5}, {5, 15, 20, 15, 5, 0}},
		routersCount:    2,
		routerCapacity:  1000,
		reductionFactor: 0.5,
		expected:        []int{0, 3}, // Optimal placement on opposite sides
	},
	{
		description:     "Complete Network with 4 nodes, place 2 routers",
		nodes:           4,
		edges:           []Edge{{0, 1, 10}, {0, 2, 15}, {0, 3, 20}, {1, 2, 25}, {1, 3, 30}, {2, 3, 35}},
		demand:          [][]int{{0, 10, 20, 30}, {10, 0, 15, 25}, {20, 15, 0, 35}, {30, 25, 35, 0}},
		routersCount:    2,
		routerCapacity:  1000,
		reductionFactor: 0.5,
		expected:        []int{0, 3}, // Nodes with highest total demand
	},
	{
		description:     "Capacity Constrained Network",
		nodes:           5,
		edges:           []Edge{{0, 1, 10}, {1, 2, 15}, {2, 3, 20}, {3, 4, 25}},
		demand:          [][]int{{0, 100, 100, 100, 100}, {100, 0, 100, 100, 100}, {100, 100, 0, 100, 100}, {100, 100, 100, 0, 100}, {100, 100, 100, 100, 0}},
		routersCount:    2,
		routerCapacity:  1200, // Low capacity, can't handle all traffic
		reductionFactor: 0.5,
		expected:        []int{1, 3}, // Strategic placement to handle capacity constraints
	},
	{
		description:     "Large Network Test",
		nodes:           8,
		edges:           []Edge{{0, 1, 10}, {1, 2, 15}, {2, 3, 10}, {3, 4, 15}, {4, 5, 10}, {5, 6, 15}, {6, 7, 10}, {0, 7, 15}, {1, 7, 20}, {2, 6, 20}},
		demand:          [][]int{{0, 50, 40, 30, 20, 30, 40, 50}, {50, 0, 50, 40, 30, 20, 30, 40}, {40, 50, 0, 50, 40, 30, 20, 30}, {30, 40, 50, 0, 50, 40, 30, 20}, {20, 30, 40, 50, 0, 50, 40, 30}, {30, 20, 30, 40, 50, 0, 50, 40}, {40, 30, 20, 30, 40, 50, 0, 50}, {50, 40, 30, 20, 30, 40, 50, 0}},
		routersCount:    3,
		routerCapacity:  2000,
		reductionFactor: 0.5,
		expected:        []int{1, 3, 5}, // Strategic placement across the network
	},
	{
		description:     "No Solution (Capacity Too Small)",
		nodes:           4,
		edges:           []Edge{{0, 1, 10}, {1, 2, 10}, {2, 3, 10}},
		demand:          [][]int{{0, 100, 100, 100}, {100, 0, 100, 100}, {100, 100, 0, 100}, {100, 100, 100, 0}},
		routersCount:    1,
		routerCapacity:  10, // Extremely low capacity
		reductionFactor: 0.5,
		expected:        []int{}, // No solution possible
	},
}