package network_partition

import (
	"math"
)

// NetworkPartition partitions the network into k disjoint subnetworks.
// It returns an assignment slice where assignment[i] is the subnetwork ID for server i.
// If no valid partition exists, it returns an empty slice.
func NetworkPartition(n int, k int, riskScores []int, edges [][]int) []int {
	// Initialize assignment using a simple round-robin approach.
	assignment := make([]int, n)
	binCount := make([]int, k)
	binSums := make([]int, k)
	for i := 0; i < n; i++ {
		group := i % k
		assignment[i] = group
		binCount[group]++
		binSums[group] += riskScores[i]
	}

	currentRiskDiff := getRiskDiff(binSums)
	currentCommCost := computeCommCost(assignment, edges)

	improved := true
	for improved {
		improved = false
		// Try single node reassignment moves.
		for i := 0; i < n; i++ {
			origGroup := assignment[i]
			for newGroup := 0; newGroup < k; newGroup++ {
				if newGroup == origGroup {
					continue
				}
				// Do not move if it would leave the original group empty.
				if binCount[origGroup] == 1 {
					continue
				}
				// Update bin sums for the tentative move.
				newBinSums := make([]int, k)
				copy(newBinSums, binSums)
				newBinSums[origGroup] -= riskScores[i]
				newBinSums[newGroup] += riskScores[i]
				newRiskDiff := getRiskDiff(newBinSums)
				// Skip if risk difference worsens.
				if newRiskDiff > currentRiskDiff {
					continue
				}
				// Create a tentative assignment.
				newAssignment := make([]int, n)
				copy(newAssignment, assignment)
				newAssignment[i] = newGroup
				newCommCost := computeCommCost(newAssignment, edges)
				// Accept the move if either the risk difference improves, or if equal, communication cost improves.
				if newRiskDiff < currentRiskDiff || (newRiskDiff == currentRiskDiff && newCommCost < currentCommCost) {
					assignment[i] = newGroup
					binSums[origGroup] -= riskScores[i]
					binSums[newGroup] += riskScores[i]
					binCount[origGroup]--
					binCount[newGroup]++
					currentRiskDiff = newRiskDiff
					currentCommCost = newCommCost
					improved = true
					goto Restart
				}
			}
		}

		// Try pair-swap moves.
		for i := 0; i < n; i++ {
			for j := i + 1; j < n; j++ {
				if assignment[i] == assignment[j] {
					continue
				}
				grpI := assignment[i]
				grpJ := assignment[j]
				// Do not swap if it would empty any group.
				if binCount[grpI] == 1 || binCount[grpJ] == 1 {
					continue
				}
				newBinSums := make([]int, k)
				copy(newBinSums, binSums)
				newBinSums[grpI] = newBinSums[grpI] - riskScores[i] + riskScores[j]
				newBinSums[grpJ] = newBinSums[grpJ] - riskScores[j] + riskScores[i]
				newRiskDiff := getRiskDiff(newBinSums)
				if newRiskDiff > currentRiskDiff {
					continue
				}
				newAssignment := make([]int, n)
				copy(newAssignment, assignment)
				newAssignment[i], newAssignment[j] = newAssignment[j], newAssignment[i]
				newCommCost := computeCommCost(newAssignment, edges)
				if newRiskDiff < currentRiskDiff || (newRiskDiff == currentRiskDiff && newCommCost < currentCommCost) {
					assignment[i], assignment[j] = assignment[j], assignment[i]
					binSums[grpI] = newBinSums[grpI]
					binSums[grpJ] = newBinSums[grpJ]
					currentRiskDiff = newRiskDiff
					currentCommCost = newCommCost
					improved = true
					goto Restart
				}
			}
		}
	Restart:
	}
	// Validate that every subnetwork is non-empty.
	groupPresent := make([]bool, k)
	for _, grp := range assignment {
		groupPresent[grp] = true
	}
	for group := 0; group < k; group++ {
		if !groupPresent[group] {
			return []int{}
		}
	}
	return assignment
}

func getRiskDiff(binSums []int) int {
	minSum := math.MaxInt32
	maxSum := 0
	for _, sum := range binSums {
		if sum < minSum {
			minSum = sum
		}
		if sum > maxSum {
			maxSum = sum
		}
	}
	return maxSum - minSum
}

func computeCommCost(assignment []int, edges [][]int) int {
	cost := 0
	for _, edge := range edges {
		if assignment[edge[0]] != assignment[edge[1]] {
			cost++
		}
	}
	return cost
}