package optimal_pathways

var testCases = []struct {
	description    string
	n             int
	edges         [][]int
	start         int
	destinations  []int
	expected      []int
}{
	{
		description: "simple path with single destination",
		n:           3,
		edges: [][]int{
			{0, 1, 2},
			{1, 2, 3},
		},
		start:        0,
		destinations: []int{2},
		expected:     []int{3},
	},
	{
		description: "path with multiple destinations",
		n:           4,
		edges: [][]int{
			{0, 1, 2},
			{1, 2, 3},
			{2, 3, 4},
		},
		start:        0,
		destinations: []int{2, 3},
		expected:     []int{3, 4},
	},
	{
		description: "path with unreachable destination",
		n:           4,
		edges: [][]int{
			{0, 1, 2},
			{2, 3, 3},
		},
		start:        0,
		destinations: []int{3},
		expected:     []int{-1},
	},
	{
		description:   "empty graph",
		n:            1,
		edges:        [][]int{},
		start:        0,
		destinations: []int{0},
		expected:     []int{0},
	},
}