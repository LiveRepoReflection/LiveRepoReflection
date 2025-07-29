package dtc

type testCase struct {
	description string
	services    int
	minValue    int
	maxValue    int
	lossProb    float64
	deltas      [][]int
	expected    []int
}

var basicTests = []testCase{
	{
		description: "simple transaction",
		services:    3,
		minValue:    0,
		maxValue:    100,
		lossProb:    0.0,
		deltas:      [][]int{{10, 20, 30}},
		expected:    []int{10, 20, 30},
	},
	{
		description: "multiple transactions",
		services:    2,
		minValue:    0,
		maxValue:    100,
		lossProb:    0.0,
		deltas:      [][]int{{10, 20}, {5, 5}},
		expected:    []int{15, 25},
	},
	{
		description: "boundary test",
		services:    2,
		minValue:    0,
		maxValue:    50,
		lossProb:    0.0,
		deltas:      [][]int{{50, 50}, {1, 1}},
		expected:    []int{50, 50},
	},
}

var errorTests = []testCase{
	{
		description: "violation of upper bound",
		services:    2,
		minValue:    0,
		maxValue:    100,
		lossProb:    0.0,
		deltas:      [][]int{{101, 50}},
		expected:    []int{0, 0},
	},
	{
		description: "violation of lower bound",
		services:    2,
		minValue:    0,
		maxValue:    100,
		lossProb:    0.0,
		deltas:      [][]int{{10, 10}, {-20, -5}},
		expected:    []int{10, 10},
	},
}
