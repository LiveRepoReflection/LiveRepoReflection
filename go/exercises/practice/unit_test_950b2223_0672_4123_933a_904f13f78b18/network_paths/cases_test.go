package networkpaths

var testCases = []struct {
	description string
	edges       [][]int
	operations  []struct {
		name   string
		args   []interface{}
		expect interface{}
	}
}{
	{
		description: "basic network with single path",
		edges: [][]int{
			{1, 2, 10},
			{2, 3, 5},
		},
		operations: []struct {
			name   string
			args   []interface{}
			expect interface{}
		}{
			{
				name:   "FindLowestLatencyPath",
				args:   []interface{}{1, 3},
				expect: []interface{}{15, []int{1, 2, 3}},
			},
		},
	},
	{
		description: "network with multiple paths",
		edges: [][]int{
			{1, 2, 1},
			{2, 3, 4},
			{1, 3, 10},
		},
		operations: []struct {
			name   string
			args   []interface{}
			expect interface{}
		}{
			{
				name:   "FindLowestLatencyPath",
				args:   []interface{}{1, 3},
				expect: []interface{}{5, []int{1, 2, 3}},
			},
		},
	},
	{
		description: "network with disabled router",
		edges: [][]int{
			{1, 2, 1},
			{2, 3, 1},
			{1, 3, 5},
		},
		operations: []struct {
			name   string
			args   []interface{}
			expect interface{}
		}{
			{
				name: "DisableRouter",
				args: []interface{}{2},
			},
			{
				name:   "FindLowestLatencyPath",
				args:   []interface{}{1, 3},
				expect: []interface{}{5, []int{1, 3}},
			},
		},
	},
	{
		description: "disconnected network",
		edges: [][]int{
			{1, 2, 1},
			{3, 4, 1},
		},
		operations: []struct {
			name   string
			args   []interface{}
			expect interface{}
		}{
			{
				name:   "FindLowestLatencyPath",
				args:   []interface{}{1, 4},
				expect: []interface{}{-1, []int{}},
			},
		},
	},
	{
		description: "network with edge modifications",
		edges: [][]int{
			{1, 2, 10},
			{2, 3, 10},
		},
		operations: []struct {
			name   string
			args   []interface{}
			expect interface{}
		}{
			{
				name: "AddEdge",
				args: []interface{}{1, 3, 15},
			},
			{
				name:   "FindLowestLatencyPath",
				args:   []interface{}{1, 3},
				expect: []interface{}{15, []int{1, 3}},
			},
			{
				name: "RemoveEdge",
				args: []interface{}{1, 2},
			},
			{
				name:   "FindLowestLatencyPath",
				args:   []interface{}{1, 3},
				expect: []interface{}{15, []int{1, 3}},
			},
		},
	},
}