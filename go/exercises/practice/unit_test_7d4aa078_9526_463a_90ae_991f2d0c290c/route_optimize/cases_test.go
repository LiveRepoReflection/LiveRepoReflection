package route_optimize

type testCase struct {
	description string
	graph      map[int][]Edge
	start      int
	end        int
	deadline   int
	expected   []int
}

var testCases = []testCase{
	{
		description: "simple direct route",
		graph: map[int][]Edge{
			0: {{To: 1, Cost: 5, Priority: 3}},
			1: {},
		},
		start:    0,
		end:      1,
		deadline: 10,
		expected: []int{0, 1},
	},
	{
		description: "no route exists",
		graph: map[int][]Edge{
			0: {{To: 1, Cost: 5, Priority: 3}},
			1: {},
			2: {},
		},
		start:    0,
		end:      2,
		deadline: 10,
		expected: []int{},
	},
	{
		description: "multiple routes with different priorities",
		graph: map[int][]Edge{
			0: {
				{To: 1, Cost: 5, Priority: 3},
				{To: 2, Cost: 3, Priority: 2},
			},
			1: {{To: 3, Cost: 2, Priority: 4}},
			2: {{To: 3, Cost: 4, Priority: 1}},
			3: {},
		},
		start:    0,
		end:      3,
		deadline: 10,
		expected: []int{0, 1, 3},
	},
	{
		description: "same start and end",
		graph: map[int][]Edge{
			0: {},
		},
		start:    0,
		end:      0,
		deadline: 10,
		expected: []int{0},
	},
	{
		description: "complex graph with multiple options",
		graph: map[int][]Edge{
			0: {
				{To: 1, Cost: 2, Priority: 5},
				{To: 2, Cost: 4, Priority: 6},
			},
			1: {
				{To: 3, Cost: 5, Priority: 4},
				{To: 4, Cost: 3, Priority: 7},
			},
			2: {
				{To: 4, Cost: 2, Priority: 5},
				{To: 5, Cost: 6, Priority: 3},
			},
			3: {{To: 5, Cost: 1, Priority: 8}},
			4: {{To: 5, Cost: 2, Priority: 5}},
			5: {},
		},
		start:    0,
		end:      5,
		deadline: 10,
		expected: []int{0, 1, 4, 5},
	},
	{
		description: "route exceeds deadline",
		graph: map[int][]Edge{
			0: {{To: 1, Cost: 15, Priority: 5}},
			1: {},
		},
		start:    0,
		end:      1,
		deadline: 10,
		expected: []int{},
	},
	{
		description: "multiple edges between same nodes",
		graph: map[int][]Edge{
			0: {
				{To: 1, Cost: 3, Priority: 2},
				{To: 1, Cost: 4, Priority: 5},
				{To: 1, Cost: 2, Priority: 3},
			},
			1: {},
		},
		start:    0,
		end:      1,
		deadline: 5,
		expected: []int{0, 1},
	},
	{
		description: "tie breaker - same min priority, choose lower cost",
		graph: map[int][]Edge{
			0: {
				{To: 1, Cost: 3, Priority: 5},
				{To: 2, Cost: 2, Priority: 5},
			},
			1: {{To: 3, Cost: 2, Priority: 4}},
			2: {{To: 3, Cost: 3, Priority: 4}},
			3: {},
		},
		start:    0,
		end:      3,
		deadline: 10,
		expected: []int{0, 2, 3},
	},
	{
		description: "tie breaker - same min priority and cost, choose shorter path",
		graph: map[int][]Edge{
			0: {
				{To: 1, Cost: 2, Priority: 5},
				{To: 2, Cost: 2, Priority: 5},
			},
			1: {{To: 3, Cost: 2, Priority: 5}},
			2: {{To: 3, Cost: 2, Priority: 5}},
			3: {},
		},
		start:    0,
		end:      3,
		deadline: 10,
		expected: []int{0, 1, 3},
	},
}