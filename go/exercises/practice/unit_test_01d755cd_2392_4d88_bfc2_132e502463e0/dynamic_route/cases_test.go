package dynamic_route

var testCases = []struct {
	name        string
	N           int
	T           int
	snapshots   [][][]int
	queries     [][4]int
	expected    []int
	expectError bool
}{
	{
		name: "single node network",
		N:    1,
		T:    1,
		snapshots: [][][]int{
			{},
		},
		queries: [][4]int{
			{0, 0, 0, 0},
		},
		expected:    []int{0},
		expectError: false,
	},
	{
		name: "disconnected network",
		N:    3,
		T:    2,
		snapshots: [][][]int{
			{{0, 1, 1}},
			{{1, 2, 1}},
		},
		queries: [][4]int{
			{0, 2, 0, 0},
		},
		expected:    []int{-1},
		expectError: false,
	},
	{
		name: "large time window",
		N:    4,
		T:    5,
		snapshots: [][][]int{
			{{0, 1, 5}},
			{{1, 2, 5}},
			{{2, 3, 5}},
			{{0, 3, 10}},
			{{0, 2, 15}},
		},
		queries: [][4]int{
			{0, 3, 0, 4},
		},
		expected:    []int{10},
		expectError: false,
	},
}