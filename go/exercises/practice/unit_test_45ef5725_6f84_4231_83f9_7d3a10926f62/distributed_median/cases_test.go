package distributed_median

var testCases = []struct {
	description string
	workerBuffers [][]int
	expectedMedian float64
}{
	{
		description: "single worker with odd count",
		workerBuffers: [][]int{{1, 2, 3, 4, 5}},
		expectedMedian: 3.0,
	},
	{
		description: "single worker with even count",
		workerBuffers: [][]int{{1, 2, 3, 4}},
		expectedMedian: 2.5,
	},
	{
		description: "multiple workers with odd total count",
		workerBuffers: [][]int{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}},
		expectedMedian: 5.0,
	},
	{
		description: "multiple workers with even total count",
		workerBuffers: [][]int{{1, 2}, {3, 4}, {5, 6}},
		expectedMedian: 3.5,
	},
	{
		description: "duplicate values across workers",
		workerBuffers: [][]int{{1, 1, 2}, {2, 3, 3}, {4, 4, 4}},
		expectedMedian: 3.0,
	},
	{
		description: "large number of workers",
		workerBuffers: [][]int{
			{1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12},
			{13, 14, 15}, {16, 17, 18}, {19, 20, 21},
		},
		expectedMedian: 11.0,
	},
	{
		description: "empty buffers",
		workerBuffers: [][]int{{}, {}, {}},
		expectedMedian: 0.0,
	},
	{
		description: "mixed empty and non-empty buffers",
		workerBuffers: [][]int{{}, {1, 2, 3}, {}},
		expectedMedian: 2.0,
	},
}