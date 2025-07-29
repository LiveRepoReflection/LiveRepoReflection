package constrained_path

var testCases = []struct {
	description string
	n           int
	edges       [][]int
	start       int
	destination int
	maxRisk     int
	expected    int
}{
	{
		description: "simple path with low risk",
		n:           3,
		edges:       [][]int{{0, 1, 5, 2}, {1, 2, 3, 1}, {0, 2, 10, 4}},
		start:       0,
		destination: 2,
		maxRisk:     3,
		expected:    8,
	},
	{
		description: "no path within risk limit",
		n:           4,
		edges:       [][]int{{0, 1, 2, 5}, {1, 2, 3, 6}, {0, 2, 7, 4}},
		start:       0,
		destination: 2,
		maxRisk:     3,
		expected:    -1,
	},
	{
		description: "multiple paths with varying risk",
		n:           5,
		edges:       [][]int{{0, 1, 5, 2}, {0, 2, 3, 1}, {1, 3, 6, 3}, {2, 3, 2, 2}, {3, 4, 4, 1}, {0, 4, 15, 5}},
		start:       0,
		destination: 4,
		maxRisk:     8,
		expected:    9,
	},
	{
		description: "large risk budget",
		n:           4,
		edges:       [][]int{{0, 1, 1, 100}, {1, 2, 1, 100}, {2, 3, 1, 100}},
		start:       0,
		destination: 3,
		maxRisk:     1000,
		expected:    3,
	},
	{
		description: "start equals destination",
		n:           3,
		edges:       [][]int{{0, 1, 5, 2}, {1, 2, 3, 1}},
		start:       2,
		destination: 2,
		maxRisk:     10,
		expected:    0,
	},
	{
		description: "disconnected graph",
		n:           4,
		edges:       [][]int{{0, 1, 2, 1}, {2, 3, 3, 2}},
		start:       0,
		destination: 3,
		maxRisk:     10,
		expected:    -1,
	},
	{
		description: "multiple edges between nodes",
		n:           2,
		edges:       [][]int{{0, 1, 5, 3}, {0, 1, 3, 5}, {0, 1, 4, 4}},
		start:       0,
		destination: 1,
		maxRisk:     4,
		expected:    4,
	},
}