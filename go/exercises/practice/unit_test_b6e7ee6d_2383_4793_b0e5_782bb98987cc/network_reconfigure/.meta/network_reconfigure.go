package network_reconfigure

// ReconfigureNetwork calculates the minimum cost to transform the initial network topology (adjMatrix)
// into the target topology (targetAdjMatrix) using the costAdd and costRemove matrices.
// It iterates over all unique pairs (i, j) where i < j and accumulates the cost for each necessary operation.
// In case an operation is required but marked as impossible (cost == -1), it returns -1 indicating no valid solution.
func ReconfigureNetwork(adjMatrix [][]bool, targetAdjMatrix [][]bool, costAdd [][]int, costRemove [][]int) int {
	n := len(adjMatrix)
	totalCost := 0

	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			current := adjMatrix[i][j]
			target := targetAdjMatrix[i][j]
			if current == target {
				continue
			}
			if target {
				// Need to add an edge.
				if costAdd[i][j] == -1 {
					return -1
				}
				totalCost += costAdd[i][j]
			} else {
				// Need to remove an edge.
				if costRemove[i][j] == -1 {
					return -1
				}
				totalCost += costRemove[i][j]
			}
		}
	}

	return totalCost
}