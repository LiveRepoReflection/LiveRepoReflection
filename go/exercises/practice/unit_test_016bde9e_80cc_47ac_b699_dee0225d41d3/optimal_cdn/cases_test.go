package optimal_cdn

// TestCases represents the test cases for the CDN optimization problem
var testCases = []struct {
	name                 string
	n, m, k, p           int
	c, t                 int
	connections          [][3]int
	users                [][2]int
	originLatencies      []int
	expectedMinimumCost  int
	expectError          bool
}{
	{
		name:            "Basic Example",
		n:               5,
		m:               6,
		k:               2,
		p:               1,
		c:               100,
		t:               20,
		connections: [][3]int{
			{0, 1, 5},
			{0, 2, 10},
			{1, 2, 3},
			{1, 3, 8},
			{2, 4, 7},
			{3, 4, 2},
		},
		users: [][2]int{
			{1, 50},
			{4, 30},
		},
		originLatencies:     []int{0, 12, 15, 18, 9},
		expectedMinimumCost: 760, // Example value, might need adjustment based on correct answer
	},
	{
		name:            "Simple Network",
		n:               3,
		m:               3,
		k:               1,
		p:               1,
		c:               50,
		t:               10,
		connections: [][3]int{
			{0, 1, 5},
			{0, 2, 8},
			{1, 2, 3},
		},
		users: [][2]int{
			{2, 100},
		},
		originLatencies:     []int{0, 5, 8},
		expectedMinimumCost: 450, // Example value
	},
	{
		name:            "Linear Network",
		n:               5,
		m:               4,
		k:               3,
		p:               2,
		c:               200,
		t:               15,
		connections: [][3]int{
			{0, 1, 10},
			{1, 2, 10},
			{2, 3, 10},
			{3, 4, 10},
		},
		users: [][2]int{
			{1, 20},
			{3, 30},
			{4, 50},
		},
		originLatencies:     []int{0, 10, 20, 30, 40},
		expectedMinimumCost: 1400, // Example value
	},
	{
		name:            "Disconnected Graph",
		n:               6,
		m:               4,
		k:               2,
		p:               2,
		c:               150,
		t:               25,
		connections: [][3]int{
			{0, 1, 10},
			{1, 2, 15},
			{3, 4, 5},
			{4, 5, 10},
		},
		users: [][2]int{
			{2, 40},
			{5, 60},
		},
		originLatencies:     []int{0, 10, 25, 100, 80, 70},
		expectedMinimumCost: 8400, // Example value
	},
	{
		name:            "Dense Network",
		n:               4,
		m:               6,
		k:               3,
		p:               1,
		c:               300,
		t:               20,
		connections: [][3]int{
			{0, 1, 5},
			{0, 2, 10},
			{0, 3, 15},
			{1, 2, 7},
			{1, 3, 12},
			{2, 3, 8},
		},
		users: [][2]int{
			{1, 25},
			{2, 35},
			{3, 45},
		},
		originLatencies:     []int{0, 5, 10, 15},
		expectedMinimumCost: 1050, // Example value
	},
	{
		name:            "High Request Rate",
		n:               3,
		m:               2,
		k:               1,
		p:               1,
		c:               500,
		t:               30,
		connections: [][3]int{
			{0, 1, 20},
			{1, 2, 25},
		},
		users: [][2]int{
			{2, 1000},
		},
		originLatencies:     []int{0, 20, 45},
		expectedMinimumCost: 25500, // Example value
	},
	{
		name:            "Multiple Servers Required",
		n:               7,
		m:               10,
		k:               4,
		p:               3,
		c:               200,
		t:               15,
		connections: [][3]int{
			{0, 1, 5},
			{0, 2, 10},
			{1, 3, 8},
			{2, 4, 12},
			{3, 5, 7},
			{4, 6, 9},
			{1, 2, 6},
			{3, 4, 11},
			{5, 6, 13},
			{0, 6, 20},
		},
		users: [][2]int{
			{3, 100},
			{4, 150},
			{5, 200},
			{6, 250},
		},
		originLatencies:     []int{0, 5, 10, 13, 22, 20, 20},
		expectedMinimumCost: 5700, // Example value
	},
	{
		name:            "No Servers Placement",
		n:               4,
		m:               3,
		k:               2,
		p:               0,
		c:               1000,
		t:               50,
		connections: [][3]int{
			{0, 1, 10},
			{0, 2, 20},
			{0, 3, 30},
		},
		users: [][2]int{
			{1, 50},
			{3, 70},
		},
		originLatencies:     []int{0, 10, 20, 30},
		expectedMinimumCost: 2600, // Example value (pure latency cost to origin)
	},
	{
		name:            "Multiple Connections Between Cities",
		n:               4,
		m:               5,
		k:               2,
		p:               1,
		c:               200,
		t:               25,
		connections: [][3]int{
			{0, 1, 15},
			{0, 1, 10}, // Duplicate connection with different latency
			{1, 2, 12},
			{2, 3, 8},
			{0, 3, 25},
		},
		users: [][2]int{
			{2, 80},
			{3, 120},
		},
		originLatencies:     []int{0, 10, 22, 25},
		expectedMinimumCost: 1640, // Example value
	},
	{
		name:            "Edge Case: Latency Equal To Threshold",
		n:               3,
		m:               2,
		k:               1,
		p:               1,
		c:               100,
		t:               20,
		connections: [][3]int{
			{0, 1, 10},
			{1, 2, 20},
		},
		users: [][2]int{
			{2, 40},
		},
		originLatencies:     []int{0, 10, 30},
		expectedMinimumCost: 900, // Example value
	},
}