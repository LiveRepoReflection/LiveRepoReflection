package taskscheduler

// Test cases for the task scheduler
var testCases = []struct {
	description string
	tasks       []Task
	wantOrder   []int
	wantSpan    int
	wantFeasible bool
}{
	{
		description: "single task",
		tasks: []Task{
			{ID: 0, Duration: 1, Deadline: 10, Dependencies: []int{}},
		},
		wantOrder:    []int{0},
		wantSpan:     1,
		wantFeasible: true,
	},
	{
		description: "two independent tasks",
		tasks: []Task{
			{ID: 0, Duration: 2, Deadline: 10, Dependencies: []int{}},
			{ID: 1, Duration: 3, Deadline: 10, Dependencies: []int{}},
		},
		wantOrder:    []int{0, 1},
		wantSpan:     5,
		wantFeasible: true,
	},
	{
		description: "simple dependency chain",
		tasks: []Task{
			{ID: 0, Duration: 2, Deadline: 10, Dependencies: []int{1}},
			{ID: 1, Duration: 3, Deadline: 5, Dependencies: []int{}},
		},
		wantOrder:    []int{1, 0},
		wantSpan:     5,
		wantFeasible: true,
	},
	{
		description: "impossible deadline",
		tasks: []Task{
			{ID: 0, Duration: 5, Deadline: 3, Dependencies: []int{}},
		},
		wantOrder:    []int{},
		wantSpan:     0,
		wantFeasible: false,
	},
	{
		description: "cyclic dependency",
		tasks: []Task{
			{ID: 0, Duration: 2, Deadline: 10, Dependencies: []int{1}},
			{ID: 1, Duration: 3, Deadline: 10, Dependencies: []int{0}},
		},
		wantOrder:    []int{},
		wantSpan:     0,
		wantFeasible: false,
	},
	{
		description: "complex dependency graph",
		tasks: []Task{
			{ID: 0, Duration: 2, Deadline: 20, Dependencies: []int{1, 2}},
			{ID: 1, Duration: 3, Deadline: 10, Dependencies: []int{3}},
			{ID: 2, Duration: 4, Deadline: 15, Dependencies: []int{3}},
			{ID: 3, Duration: 1, Deadline: 5, Dependencies: []int{}},
		},
		wantOrder:    []int{3, 1, 2, 0},
		wantSpan:     10,
		wantFeasible: true,
	},
	{
		description: "tight deadlines",
		tasks: []Task{
			{ID: 0, Duration: 2, Deadline: 2, Dependencies: []int{}},
			{ID: 1, Duration: 3, Deadline: 5, Dependencies: []int{0}},
		},
		wantOrder:    []int{0, 1},
		wantSpan:     5,
		wantFeasible: true,
	},
	{
		description: "multiple valid solutions",
		tasks: []Task{
			{ID: 0, Duration: 1, Deadline: 10, Dependencies: []int{}},
			{ID: 1, Duration: 1, Deadline: 10, Dependencies: []int{}},
			{ID: 2, Duration: 1, Deadline: 10, Dependencies: []int{}},
		},
		wantSpan:     3,
		wantFeasible: true,
	},
}
