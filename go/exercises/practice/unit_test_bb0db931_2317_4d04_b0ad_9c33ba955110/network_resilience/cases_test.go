package resilience

type testCase struct {
	description string
	n          int
	adjMatrix  [][]int
	data       []nodeData
	expected   bool
}

var resilienceTests = []testCase{
	{
		description: "small network with single component - resilient",
		n:          4,
		adjMatrix: [][]int{
			{0, 1, 0, 0},
			{1, 0, 1, 0},
			{0, 1, 0, 0},
			{0, 0, 0, 0},
		},
		data: []nodeData{
			{NodeID: 0, DataID: 123, Version: 5},
			{NodeID: 1, DataID: 123, Version: 5},
			{NodeID: 2, DataID: 123, Version: 5},
			{NodeID: 3, DataID: 456, Version: 1},
		},
		expected: true,
	},
	{
		description: "network with inconsistent data - not resilient",
		n:          3,
		adjMatrix: [][]int{
			{0, 1, 1},
			{1, 0, 1},
			{1, 1, 0},
		},
		data: []nodeData{
			{NodeID: 0, DataID: 123, Version: 5},
			{NodeID: 1, DataID: 123, Version: 6},
			{NodeID: 2, DataID: 123, Version: 5},
		},
		expected: false,
	},
	{
		description: "single node network - resilient",
		n:          1,
		adjMatrix: [][]int{
			{0},
		},
		data: []nodeData{
			{NodeID: 0, DataID: 123, Version: 5},
		},
		expected: true,
	},
	{
		description: "disconnected network with equal components - choose lowest NodeID",
		n:          4,
		adjMatrix: [][]int{
			{0, 1, 0, 0},
			{1, 0, 0, 0},
			{0, 0, 0, 1},
			{0, 0, 1, 0},
		},
		data: []nodeData{
			{NodeID: 0, DataID: 123, Version: 5},
			{NodeID: 1, DataID: 123, Version: 5},
			{NodeID: 2, DataID: 456, Version: 7},
			{NodeID: 3, DataID: 456, Version: 7},
		},
		expected: true,
	},
	{
		description: "large network with multiple components",
		n:          6,
		adjMatrix: [][]int{
			{0, 1, 1, 0, 0, 0},
			{1, 0, 1, 0, 0, 0},
			{1, 1, 0, 0, 0, 0},
			{0, 0, 0, 0, 1, 1},
			{0, 0, 0, 1, 0, 1},
			{0, 0, 0, 1, 1, 0},
		},
		data: []nodeData{
			{NodeID: 0, DataID: 123, Version: 5},
			{NodeID: 1, DataID: 123, Version: 5},
			{NodeID: 2, DataID: 123, Version: 5},
			{NodeID: 3, DataID: 456, Version: 7},
			{NodeID: 4, DataID: 456, Version: 7},
			{NodeID: 5, DataID: 456, Version: 7},
		},
		expected: true,
	},
}