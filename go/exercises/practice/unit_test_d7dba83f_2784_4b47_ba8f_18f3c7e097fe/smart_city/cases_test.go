package smart_city

// Test case data structures for additional test cases

var complexTestCases = []struct {
	name            string
	N               int
	M               int
	channels        [][4]int
	dataSources     [][5]interface{}
	simulationTime  int
	expectedScore   int
}{
	{
		name: "large network with mixed priorities",
		N:    10,
		M:    20,
		channels: [][4]int{
			{1, 0, 30, 3}, {2, 0, 25, 5}, {3, 0, 20, 2},
			{4, 1, 15, 4}, {5, 1, 10, 3}, {6, 2, 20, 2},
			{7, 2, 25, 3}, {8, 3, 15, 1}, {9, 3, 10, 2},
			{4, 2, 20, 3}, {5, 3, 15, 2}, {6, 4, 10, 4},
			{7, 5, 25, 3}, {8, 6, 15, 2}, {9, 7, 20, 1},
			{1, 2, 30, 2}, {2, 3, 25, 3}, {3, 4, 20, 4},
			{4, 5, 15, 1}, {5, 6, 10, 2},
		},
		dataSources: [][5]interface{}{
			{4, "LowPriority", 3, 15, 8},
			{5, "MediumPriority", 6, 10, 6},
			{6, "HighPriority", 9, 8, 5},
			{7, "Critical", 10, 5, 4},
			{8, "LowPriority", 2, 20, 10},
			{9, "MediumPriority", 5, 12, 7},
		},
		simulationTime: 2,
		expectedScore:  38,
	},
	{
		name: "network with multiple possible paths",
		N:    6,
		M:    8,
		channels: [][4]int{
			{1, 0, 20, 3}, {2, 0, 15, 5},
			{3, 1, 25, 2}, {4, 1, 10, 4},
			{5, 2, 15, 3}, {3, 2, 20, 2},
			{4, 3, 10, 1}, {5, 4, 15, 2},
		},
		dataSources: [][5]interface{}{
			{3, "DataA", 7, 8, 5},
			{4, "DataB", 5, 10, 8},
			{5, "DataC", 8, 6, 4},
		},
		simulationTime: 1,
		expectedScore:  15,
	},
}