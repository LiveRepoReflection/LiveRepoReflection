package rideshare_network

var nodeDiscoveryTests = []struct {
	name         string
	adjacencyList map[int][]int
	startNode    int
	maxDistance  int
	expected     []int
}{
	{
		name: "single node",
		adjacencyList: map[int][]int{1: {}},
		startNode:    1,
		maxDistance: 2,
		expected:    []int{1},
	},
	{
		name: "linear network",
		adjacencyList: map[int][]int{
			1: {2},
			2: {1, 3},
			3: {2, 4},
			4: {3},
		},
		startNode:    2,
		maxDistance: 1,
		expected:    []int{1, 2, 3},
	},
	{
		name: "disconnected nodes",
		adjacencyList: map[int][]int{
			1: {2},
			2: {1},
			3: {4},
			4: {3},
		},
		startNode:    1,
		maxDistance: 3,
		expected:    []int{1, 2},
	},
}

var rideMatchingTests = []struct {
	name             string
	adjacencyList    map[int][]int
	riderNode       int
	driverNodes     []int
	riderDestination int
	expected        int
}{
	{
		name: "single driver",
		adjacencyList: map[int][]int{
			1: {2},
			2: {1, 3},
			3: {2},
		},
		riderNode:       1,
		driverNodes:    []int{3},
		riderDestination: 2,
		expected:      3,
	},
	{
		name: "no drivers",
		adjacencyList: map[int][]int{
			1: {2},
			2: {1},
		},
		riderNode:       1,
		driverNodes:    []int{},
		riderDestination: 2,
		expected:      -1,
	},
}

var networkPartitionTests = []struct {
	name          string
	adjacencyList map[int][]int
	expected     int
}{
	{
		name: "fully connected",
		adjacencyList: map[int][]int{
			1: {2, 3},
			2: {1, 3},
			3: {1, 2},
		},
		expected: 1,
	},
	{
		name: "two components",
		adjacencyList: map[int][]int{
			1: {2},
			2: {1},
			3: {4},
			4: {3},
		},
		expected: 2,
	},
}