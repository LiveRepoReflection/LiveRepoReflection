package concurrentmedian

type medianTestCase struct {
	description string
	input       []int
	expected    []float64
}

var medianTestCases = []medianTestCase{
	{
		description: "Empty stream",
		input:       []int{},
		expected:    []float64{0.0},
	},
	{
		description: "Single element",
		input:       []int{5},
		expected:    []float64{5.0},
	},
	{
		description: "Two elements",
		input:       []int{5, 3},
		expected:    []float64{4.0},
	},
	{
		description: "Odd number of elements",
		input:       []int{5, 3, 1},
		expected:    []float64{3.0},
	},
	{
		description: "Even number of elements",
		input:       []int{5, 3, 1, 4},
		expected:    []float64{3.5},
	},
	{
		description: "Duplicate numbers",
		input:       []int{5, 5, 5, 5},
		expected:    []float64{5.0},
	},
	{
		description: "Large sequence",
		input:       []int{1, 3, 5, 7, 9, 2, 4, 6, 8, 10},
		expected:    []float64{5.5},
	},
	{
		description: "Negative numbers",
		input:       []int{-5, -3, -1, -4},
		expected:    []float64{-3.5},
	},
}