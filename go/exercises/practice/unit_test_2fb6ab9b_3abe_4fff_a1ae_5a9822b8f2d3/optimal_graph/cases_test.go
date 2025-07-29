package optimalgraph

// This is an auto-generated file. Do not change it manually.

type testCase struct {
	description  string
	n            int
	capacities   []int
	generations  []int
	dependencies [][]int
	expected     [][]bool
}

var testCases = []testCase{
	{
		description:  "Basic example with 3 services",
		n:            3,
		capacities:   []int{100, 100, 100},
		generations:  []int{20, 30, 10},
		dependencies: [][]int{{1, 2}, {2}, {}},
		expected: [][]bool{
			{false, true, false},
			{false, false, true},
			{false, false, false},
		},
	},
	{
		description:  "Simple linear chain of 4 services",
		n:            4,
		capacities:   []int{100, 100, 100, 100},
		generations:  []int{20, 30, 10, 5},
		dependencies: [][]int{{1, 2, 3}, {2, 3}, {3}, {}},
		expected: [][]bool{
			{false, true, false, false},
			{false, false, true, false},
			{false, false, false, true},
			{false, false, false, false},
		},
	},
	{
		description:  "Star topology with central service",
		n:            4,
		capacities:   []int{50, 50, 100, 50},
		generations:  []int{20, 20, 10, 20},
		dependencies: [][]int{{2}, {2}, {}, {2}},
		expected: [][]bool{
			{false, false, true, false},
			{false, false, true, false},
			{false, false, false, false},
			{false, false, true, false},
		},
	},
	{
		description:  "No dependencies",
		n:            3,
		capacities:   []int{100, 100, 100},
		generations:  []int{20, 30, 10},
		dependencies: [][]int{{}, {}, {}},
		expected: [][]bool{
			{false, false, false},
			{false, false, false},
			{false, false, false},
		},
	},
	{
		description:  "Capacity constraints lead to different topology",
		n:            3,
		capacities:   []int{100, 30, 100},
		generations:  []int{20, 30, 10},
		dependencies: [][]int{{1, 2}, {2}, {}},
		expected: [][]bool{
			{false, false, true},
			{false, false, true},
			{false, false, false},
		},
	},
	{
		description:  "Complex dependencies with limited capacities",
		n:            5,
		capacities:   []int{100, 50, 60, 40, 70},
		generations:  []int{20, 30, 20, 10, 15},
		dependencies: [][]int{{1, 2, 3, 4}, {2, 3, 4}, {3, 4}, {4}, {}},
		expected: [][]bool{
			{false, true, false, false, false},
			{false, false, true, false, false},
			{false, false, false, true, false},
			{false, false, false, false, true},
			{false, false, false, false, false},
		},
	},
	{
		description:  "Test with no valid solution - overcapacity",
		n:            3,
		capacities:   []int{10, 10, 10},
		generations:  []int{20, 30, 10},  // More generation than capacity
		dependencies: [][]int{{1, 2}, {2}, {}},
		expected: [][]bool{  // All false indicates no valid solution
			{false, false, false},
			{false, false, false},
			{false, false, false},
		},
	},
	{
		description:  "Larger test with multiple valid paths",
		n:            6,
		capacities:   []int{200, 150, 100, 120, 180, 90},
		generations:  []int{50, 40, 30, 20, 60, 10},
		dependencies: [][]int{{1, 2, 3}, {2, 3, 4}, {4, 5}, {4, 5}, {5}, {}},
		expected: [][]bool{
			{false, true, false, false, false, false},
			{false, false, true, false, false, false},
			{false, false, false, false, true, false},
			{false, false, false, false, true, false},
			{false, false, false, false, false, true},
			{false, false, false, false, false, false},
		},
	},
}