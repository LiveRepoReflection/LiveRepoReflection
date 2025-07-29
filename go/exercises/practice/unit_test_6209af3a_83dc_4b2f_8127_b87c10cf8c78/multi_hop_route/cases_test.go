package multi_hop_route

var testCases = []struct {
	description   string
	N             int
	edges         [][3]int
	source        int
	destination   int
	intermediates []int
	expected      int
}{
	{
		description:   "simple path with one intermediate",
		N:             4,
		edges:         [][3]int{{0, 1, 5}, {1, 2, 3}, {2, 3, 2}, {0, 2, 8}},
		source:        0,
		destination:   3,
		intermediates: []int{1},
		expected:      10,
	},
	{
		description:   "multiple intermediates in order",
		N:             5,
		edges:         [][3]int{{0, 1, 2}, {1, 2, 3}, {2, 3, 1}, {3, 4, 4}, {0, 2, 6}, {1, 3, 5}},
		source:        0,
		destination:   4,
		intermediates: []int{1, 2},
		expected:      10,
	},
	{
		description:   "no path exists",
		N:             3,
		edges:         [][3]int{{0, 1, 1}, {2, 1, 1}},
		source:        0,
		destination:   2,
		intermediates: []int{1},
		expected:      -1,
	},
	{
		description:   "intermediate equals source",
		N:             3,
		edges:         [][3]int{{0, 1, 2}, {1, 2, 3}},
		source:        0,
		destination:   2,
		intermediates: []int{0, 1},
		expected:      5,
	},
	{
		description:   "large latency values",
		N:             4,
		edges:         [][3]int{{0, 1, 1000}, {1, 2, 1000}, {2, 3, 1000}, {0, 3, 3500}},
		source:        0,
		destination:   3,
		intermediates: []int{1, 2},
		expected:      3000,
	},
	{
		description:   "duplicate intermediates",
		N:             4,
		edges:         [][3]int{{0, 1, 1}, {1, 2, 1}, {2, 1, 1}, {1, 3, 1}},
		source:        0,
		destination:   3,
		intermediates: []int{1, 2, 1},
		expected:      4,
	},
}