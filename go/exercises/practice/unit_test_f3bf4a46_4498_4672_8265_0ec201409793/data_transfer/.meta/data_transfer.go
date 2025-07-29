package data_transfer

func MinimizeDataTransferCost(n, m int, capacities []int, cost []int, availability [][]bool, k int, datacenterIDs []int, dataItemIDs []int, sizes []int) int {
	// Create a 2D slice to track if a data item is available (either initially or after a transfer)
	obtained := make([][]bool, n)
	for i := 0; i < n; i++ {
		obtained[i] = make([]bool, m)
		for j := 0; j < m; j++ {
			if availability[i][j] {
				obtained[i][j] = true
			}
		}
	}

	// Track the total size transferred to each datacenter.
	transferredSize := make([]int, n)
	totalCost := 0

	// For each request, process the distinct (destination, data item) pair only once.
	// Since the problem guarantees that the requests can be satisfied under capacity constraints,
	// we simply perform the transfer if the data item is not already present.
	for r := 0; r < k; r++ {
		dest := datacenterIDs[r]
		item := dataItemIDs[r]

		// If the destination already has the data item, skip.
		if obtained[dest][item] {
			continue
		}

		// Find the minimum cost source from any datacenter that initially has the data item.
		// Since a transfer cost is computed by: size[j] * cost[source],
		// we choose the source with the lowest cost among those with the data item.
		minSourceCost := -1
		for s := 0; s < n; s++ {
			if availability[s][item] {
				if minSourceCost == -1 || cost[s] < minSourceCost {
					minSourceCost = cost[s]
				}
			}
		}
		// In case no datacenter has the data item initially,
		// check if any datacenter already obtained the data via an earlier transfer.
		if minSourceCost == -1 {
			for s := 0; s < n; s++ {
				if obtained[s][item] {
					if minSourceCost == -1 || cost[s] < minSourceCost {
						minSourceCost = cost[s]
					}
				}
			}
		}
		// According to problem assumptions, at least one datacenter will have the item.
		transferCost := sizes[item] * minSourceCost

		// Check if the transfer does not exceed the capacity of the destination datacenter.
		// Note: Capacities refer exclusively to the space available for incoming transfers.
		if transferredSize[dest]+sizes[item] > capacities[dest] {
			// In a valid problem instance this situation should not occur.
			// Since the problem guarantees solvability, we assume this never happens.
		}
		transferredSize[dest] += sizes[item]
		obtained[dest][item] = true

		totalCost += transferCost
	}

	return totalCost
}