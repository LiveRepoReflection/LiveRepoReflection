package networklayout

type testCase struct {
	description         string
	nodes              []int
	latencyMatrix      [][]int
	maxConnections     int
	budget             int
	requiredConnectivity int
	expectedMaxWorkload int
}

var testCases = []testCase{
	{
		description: "simple case with three nodes",
		nodes:       []int{10, 20, 30},
		latencyMatrix: [][]int{
			{0, 5, 10},
			{5, 0, 15},
			{10, 15, 0},
		},
		maxConnections:      2,
		budget:             30,
		requiredConnectivity: 2,
		expectedMaxWorkload:  30,
	},
	{
		description: "four nodes with full connectivity",
		nodes:       []int{25, 25, 25, 25},
		latencyMatrix: [][]int{
			{0, 10, 10, 10},
			{10, 0, 10, 10},
			{10, 10, 0, 10},
			{10, 10, 10, 0},
		},
		maxConnections:      3,
		budget:             60,
		requiredConnectivity: 1,
		expectedMaxWorkload:  100,
	},
	{
		description: "five nodes with limited budget",
		nodes:       []int{15, 15, 15, 15, 15},
		latencyMatrix: [][]int{
			{0, 5, 10, 15, 20},
			{5, 0, 5, 10, 15},
			{10, 5, 0, 5, 10},
			{15, 10, 5, 0, 5},
			{20, 15, 10, 5, 0},
		},
		maxConnections:      2,
		budget:             25,
		requiredConnectivity: 3,
		expectedMaxWorkload:  30,
	},
}