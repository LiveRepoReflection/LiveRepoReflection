package network

// This file contains additional test cases for the network analyzer

// Create test nodes for convenience
var testNodes = []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

// Define common test graphs for reuse in tests
var (
	smallGraph = map[int][]int{
		1: {2, 3},
		2: {4},
		3: {4, 5},
		4: {},
		5: {},
	}
	
	cycleGraph = map[int][]int{
		1: {2},
		2: {3},
		3: {4},
		4: {1},
	}
	
	disconnectedGraph = map[int][]int{
		1: {2},
		2: {3},
		3: {},
		4: {5},
		5: {6},
		6: {},
	}
)

// Sample edges for testing
var testEdges = [][]int{
	{1, 2},
	{2, 3},
	{3, 4},
	{4, 5},
	{5, 6},
}

// Test-specific latency function
func fixedLatencyFunc(source, dest int) int {
	return 42 // A fixed latency for simple testing
}

// Test-specific latency function that computes based on node values
func nodeBasedLatencyFunc(source, dest int) int {
	return source * dest
}