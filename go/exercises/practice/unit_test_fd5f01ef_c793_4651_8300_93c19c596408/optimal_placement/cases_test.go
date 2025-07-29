package optimal_placement

type testCase struct {
	description string
	n           int
	latency     [][]int
	k           int
	expected    []int
}

var testCases = []testCase{
	{
		description: "Simple network with one server",
		n:           4,
		latency: [][]int{
			{0, 1, -1, 2},
			{1, 0, 1, -1},
			{-1, 1, 0, 1},
			{2, -1, 1, 0},
		},
		k:        1,
		expected: []int{1},
	},
	{
		description: "Medium network with two servers",
		n:           5,
		latency: [][]int{
			{0, 1, -1, -1, 2},
			{1, 0, 1, -1, -1},
			{-1, 1, 0, 1, -1},
			{-1, -1, 1, 0, 1},
			{2, -1, -1, 1, 0},
		},
		k:        2,
		expected: []int{0, 3},
	},
}