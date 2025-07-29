package dist_consensus

import (
	"reflect"
	"testing"
)

func TestSimulateBasic(t *testing.T) {
	testCases := []struct {
		name           string
		initialValues  []int
		maxRounds      int
		numFailedNodes int
		partitions     [][]int
		seed           int64
		expected       []int
	}{
		{
			name:           "Single node",
			initialValues:  []int{5},
			maxRounds:      1,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{5},
		},
		{
			name:           "Three nodes with same initial value",
			initialValues:  []int{10, 10, 10},
			maxRounds:      3,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{10, 10, 10},
		},
		{
			name:           "Three nodes with different initial values",
			initialValues:  []int{10, 20, 30},
			maxRounds:      3,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{20, 20, 20},
		},
		{
			name:           "Five nodes with different initial values",
			initialValues:  []int{10, 20, 30, 40, 50},
			maxRounds:      3,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{30, 30, 30, 30, 30},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := Simulate(tc.initialValues, tc.maxRounds, tc.numFailedNodes, tc.partitions, tc.seed)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Errorf("Simulate() = %v, want %v", result, tc.expected)
			}
		})
	}
}

func TestSimulateWithFailures(t *testing.T) {
	testCases := []struct {
		name           string
		initialValues  []int
		maxRounds      int
		numFailedNodes int
		partitions     [][]int
		seed           int64
		expectedLen    int
	}{
		{
			name:           "Five nodes with two failures",
			initialValues:  []int{10, 20, 30, 40, 50},
			maxRounds:      5,
			numFailedNodes: 2,
			partitions:     [][]int{},
			seed:           42,
			expectedLen:    5,
		},
		{
			name:           "Ten nodes with five failures",
			initialValues:  []int{10, 20, 30, 40, 50, 60, 70, 80, 90, 100},
			maxRounds:      5,
			numFailedNodes: 5,
			partitions:     [][]int{},
			seed:           42,
			expectedLen:    10,
		},
		{
			name:           "All nodes fail",
			initialValues:  []int{10, 20, 30},
			maxRounds:      5,
			numFailedNodes: 3,
			partitions:     [][]int{},
			seed:           42,
			expectedLen:    3,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := Simulate(tc.initialValues, tc.maxRounds, tc.numFailedNodes, tc.partitions, tc.seed)
			if len(result) != tc.expectedLen {
				t.Errorf("Simulate() result length = %d, want %d", len(result), tc.expectedLen)
			}
		})
	}
}

func TestSimulateWithPartitions(t *testing.T) {
	testCases := []struct {
		name           string
		initialValues  []int
		maxRounds      int
		numFailedNodes int
		partitions     [][]int
		seed           int64
		expectedLen    int
	}{
		{
			name:           "Two partitions",
			initialValues:  []int{10, 20, 30, 40, 50},
			maxRounds:      5,
			numFailedNodes: 0,
			partitions:     [][]int{{0, 1, 2}, {3, 4}},
			seed:           42,
			expectedLen:    5,
		},
		{
			name:           "Three partitions",
			initialValues:  []int{10, 20, 30, 40, 50, 60},
			maxRounds:      5,
			numFailedNodes: 0,
			partitions:     [][]int{{0, 1}, {2, 3}, {4, 5}},
			seed:           42,
			expectedLen:    6,
		},
		{
			name:           "Partitions and failures",
			initialValues:  []int{10, 20, 30, 40, 50, 60, 70, 80},
			maxRounds:      5,
			numFailedNodes: 2,
			partitions:     [][]int{{0, 1, 2, 3}, {4, 5, 6, 7}},
			seed:           42,
			expectedLen:    8,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := Simulate(tc.initialValues, tc.maxRounds, tc.numFailedNodes, tc.partitions, tc.seed)
			if len(result) != tc.expectedLen {
				t.Errorf("Simulate() result length = %d, want %d", len(result), tc.expectedLen)
			}
		})
	}
}

func TestSimulateEdgeCases(t *testing.T) {
	testCases := []struct {
		name           string
		initialValues  []int
		maxRounds      int
		numFailedNodes int
		partitions     [][]int
		seed           int64
		expected       []int
	}{
		{
			name:           "Single round",
			initialValues:  []int{10, 20, 30, 40, 50},
			maxRounds:      1,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{30, 30, 30, 30, 30},
		},
		{
			name:           "Max value limits",
			initialValues:  []int{-1000, 0, 1000},
			maxRounds:      3,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{0, 0, 0},
		},
		{
			name:           "Even number of nodes (test for lower median)",
			initialValues:  []int{10, 20, 30, 40},
			maxRounds:      3,
			numFailedNodes: 0,
			partitions:     [][]int{},
			seed:           42,
			expected:       []int{20, 20, 20, 20},
		},
		{
			name:           "Empty partitions",
			initialValues:  []int{10, 20, 30},
			maxRounds:      3,
			numFailedNodes: 0,
			partitions:     [][]int{{}},
			seed:           42,
			expected:       []int{20, 20, 20},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := Simulate(tc.initialValues, tc.maxRounds, tc.numFailedNodes, tc.partitions, tc.seed)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Errorf("Simulate() = %v, want %v", result, tc.expected)
			}
		})
	}
}

func TestSimulateDeterminism(t *testing.T) {
	initialValues := []int{10, 20, 30, 40, 50}
	maxRounds := 5
	numFailedNodes := 2
	partitions := [][]int{{0, 1, 2}, {3, 4}}
	seed := int64(42)

	result1 := Simulate(initialValues, maxRounds, numFailedNodes, partitions, seed)
	result2 := Simulate(initialValues, maxRounds, numFailedNodes, partitions, seed)

	if !reflect.DeepEqual(result1, result2) {
		t.Errorf("Simulate() should be deterministic with the same seed. Got %v and %v", result1, result2)
	}
}

func BenchmarkSimulate(b *testing.B) {
	initialValues := make([]int, 100)
	for i := 0; i < 100; i++ {
		initialValues[i] = i * 10
	}
	maxRounds := 10
	numFailedNodes := 10
	partitions := [][]int{{0, 1, 2, 3, 4}, {5, 6, 7, 8, 9}}
	for i := 10; i < 100; i++ {
		if i < 50 {
			partitions[0] = append(partitions[0], i)
		} else {
			partitions[1] = append(partitions[1], i)
		}
	}
	seed := int64(42)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Simulate(initialValues, maxRounds, numFailedNodes, partitions, seed)
	}
}