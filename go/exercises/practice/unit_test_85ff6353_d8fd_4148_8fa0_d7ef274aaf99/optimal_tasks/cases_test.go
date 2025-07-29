package optimal_tasks

type taskTestCase struct {
	description string
	input       []Task
	expected    []int
}

var taskTestCases = []taskTestCase{
	{
		description: "Simple case with no dependencies",
		input: []Task{
			{1, 5, 10, []int{}},
			{2, 3, 15, []int{1}},
		},
		expected: []int{1, 2},
	},
	{
		description: "Complex case with multiple dependencies",
		input: []Task{
			{1, 5, 10, []int{}},
			{2, 3, 15, []int{1}},
			{3, 8, 20, []int{1}},
			{4, 2, 12, []int{2, 3}},
		},
		expected: []int{1, 2, 3, 4},
	},
	{
		description: "Case with tight deadlines",
		input: []Task{
			{1, 3, 5, []int{}},
			{2, 4, 6, []int{1}},
			{3, 2, 10, []int{1}},
		},
		expected: []int{1, 2, 3},
	},
	{
		description: "Case with zero duration task",
		input: []Task{
			{1, 0, 10, []int{}},
			{2, 5, 15, []int{1}},
		},
		expected: []int{1, 2},
	},
	{
		description: "Large case with many dependencies",
		input: []Task{
			{1, 2, 5, []int{}},
			{2, 3, 8, []int{1}},
			{3, 1, 10, []int{2}},
			{4, 4, 15, []int{3}},
			{5, 2, 20, []int{4}},
		},
		expected: []int{1, 2, 3, 4, 5},
	},
}