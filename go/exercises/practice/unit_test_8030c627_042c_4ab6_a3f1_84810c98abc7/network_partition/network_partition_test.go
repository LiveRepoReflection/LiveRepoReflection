package network_partition_test

import (
	"reflect"
	"testing"

	"network_partition"
)

// computeGroupRisks calculates the total risk score for each subnetwork.
func computeGroupRisks(assignment []int, riskScores []int, k int) []int {
	groupRisks := make([]int, k)
	for i, group := range assignment {
		groupRisks[group] += riskScores[i]
	}
	return groupRisks
}

// riskDifference returns the difference between the maximum and minimum risk sum.
func riskDifference(groupRisks []int) int {
	if len(groupRisks) == 0 {
		return 0
	}
	minRisk, maxRisk := groupRisks[0], groupRisks[0]
	for _, risk := range groupRisks {
		if risk < minRisk {
			minRisk = risk
		}
		if risk > maxRisk {
			maxRisk = risk
		}
	}
	return maxRisk - minRisk
}

// computeCommunicationCost calculates the communication cost based on the provided edges.
func computeCommunicationCost(assignment []int, edges [][]int) int {
	cost := 0
	for _, edge := range edges {
		// Each edge is undirected. Count an edge if endpoints belong to different groups.
		if assignment[edge[0]] != assignment[edge[1]] {
			cost++
		}
	}
	return cost
}

type testCase struct {
	name              string
	n                 int
	k                 int
	riskScores        []int
	edges             [][]int
	expectedRiskDiff  int
	expectedCommCost  int
}

func TestNetworkPartition(t *testing.T) {
	testCases := []testCase{
		{
			name:             "Simple connected graph",
			n:                3,
			k:                2,
			riskScores:       []int{1, 2, 3},
			edges:            [][]int{{0, 1}, {1, 2}},
			expectedRiskDiff: 0, // Optimal partition: group0: [0,1], group1: [2] -> risks: 1+2, 3 -> diff = 0
			expectedCommCost: 1, // One edge crossing between 1 and 2
		},
		{
			name:             "Disconnected graph",
			n:                4,
			k:                2,
			riskScores:       []int{5, 1, 2, 3},
			edges:            [][]int{}, // No edges
			expectedRiskDiff: 1, // Best possible risk difference is 1 (e.g. group0: [0], group1:[1,2,3] or similar)
			expectedCommCost: 0, // No communication cost as there are no edges
		},
		{
			name:       "Graph with multiple edges",
			n:          4,
			k:          2,
			riskScores: []int{3, 3, 7, 7},
			edges: [][]int{
				{0, 1},
				{1, 0},
				{2, 3},
				{3, 2},
				{1, 2},
				{2, 1},
			},
			expectedRiskDiff: 0, // Optimal partition: for example, group0: [0,3], group1: [1,2] => sums: 3+7=10 and 3+7=10.
			expectedCommCost: 4, // Crossing edges: [0,1], [1,0], [2,3], [3,2] cross groups; other edges are internal.
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			assignment := network_partition.NetworkPartition(tc.n, tc.k, tc.riskScores, tc.edges)
			// Check that an assignment was returned.
			if len(assignment) == 0 {
				t.Fatalf("Expected a valid partition assignment, got an empty slice")
			}
			// Check assignment length.
			if len(assignment) != tc.n {
				t.Fatalf("Expected partition length %d, got %d", tc.n, len(assignment))
			}
			// Verify that each value in the assignment is in range [0, k)
			for i, group := range assignment {
				if group < 0 || group >= tc.k {
					t.Fatalf("For server %d, expected group in [0,%d), got %d", i, tc.k, group)
				}
			}

			// Ensure that all k groups are non-empty.
			groupCount := make([]int, tc.k)
			for _, group := range assignment {
				groupCount[group]++
			}
			for i, count := range groupCount {
				if count == 0 {
					t.Fatalf("Group %d is empty; every subnetwork must have at least one server", i)
				}
			}

			// Calculate risk sums and verify risk difference.
			groupRisks := computeGroupRisks(assignment, tc.riskScores, tc.k)
			actualRiskDiff := riskDifference(groupRisks)
			if actualRiskDiff != tc.expectedRiskDiff {
				t.Errorf("Risk difference mismatch: expected %d, got %d; group risks: %v",
					tc.expectedRiskDiff, actualRiskDiff, groupRisks)
			}

			// Calculate communication cost and verify.
			actualCommCost := computeCommunicationCost(assignment, tc.edges)
			if actualCommCost != tc.expectedCommCost {
				t.Errorf("Communication cost mismatch: expected %d, got %d", tc.expectedCommCost, actualCommCost)
			}

			// Additional invariant check: The ordering of groups in the returned partition can vary.
			// For robustness, ensure that reassigning group labels still yields the same risk sums and cost.
			// Normalize the assignment by mapping the first encountered group to 0, second to 1, etc.
			mapping := make(map[int]int)
			nextLabel := 0
			normalized := make([]int, len(assignment))
			for i, group := range assignment {
				if _, exists := mapping[group]; !exists {
					mapping[group] = nextLabel
					nextLabel++
				}
				normalized[i] = mapping[group]
			}
			if !reflect.DeepEqual(normalized, assignment) {
				// Recompute metrics for normalized assignment.
				normalizedGroupRisks := computeGroupRisks(normalized, tc.riskScores, tc.k)
				normalizedRiskDiff := riskDifference(normalizedGroupRisks)
				normalizedCommCost := computeCommunicationCost(normalized, tc.edges)
				if normalizedRiskDiff != tc.expectedRiskDiff {
					t.Errorf("After normalization, risk diff mismatch: expected %d, got %d", tc.expectedRiskDiff, normalizedRiskDiff)
				}
				if normalizedCommCost != tc.expectedCommCost {
					t.Errorf("After normalization, communication cost mismatch: expected %d, got %d", tc.expectedCommCost, normalizedCommCost)
				}
			}
		})
	}
}