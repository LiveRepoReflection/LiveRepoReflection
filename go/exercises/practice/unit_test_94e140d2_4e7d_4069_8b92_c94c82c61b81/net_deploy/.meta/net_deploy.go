package net_deploy

// OptimalDeployment computes the maximum possible overall utility for deploying the service
// across a subset of data centers. It considers the processing capacities, bidirectional links,
// latencies, and a fixed deployment cost per center.
// The overall utility of a deployment subset S is defined as:
//    utility(S) = (sum of capacities for centers in S)
//                 + (total connectivity bonus)
//                 - (deployment cost per deployed center)
// The connectivity bonus for each pair of directly connected centers in S is computed as:
//    for each link between u and v included in S, add 1/latency for u and 1/latency for v.
func OptimalDeployment(capacities []int, links [][]int, latencies []int, deploymentCost int) float64 {
	n := len(capacities)
	maxUtility := 0.0
	totalSubsets := 1 << n

	// Iterate over all possible subsets of data centers represented by bitmask.
	for mask := 0; mask < totalSubsets; mask++ {
		subsetCapacity := 0
		count := 0

		// Calculate total capacity and count of selected centers in this subset.
		for i := 0; i < n; i++ {
			if mask&(1<<i) != 0 {
				subsetCapacity += capacities[i]
				count++
			}
		}

		// If the subset is empty, its utility is 0.
		if count == 0 {
			if maxUtility < 0.0 {
				maxUtility = 0.0
			}
			continue
		}

		// Calculate connectivity bonus.
		connectivityBonus := 0.0
		// For each link, if both endpoints are in the subset, add the bonus for both endpoints.
		for j, link := range links {
			if len(link) != 2 {
				continue
			}
			u := link[0]
			v := link[1]
			// Check if both data centers are in the selected subset.
			if (mask&(1<<u)) != 0 && (mask&(1<<v)) != 0 {
				latency := latencies[j]
				connectivityBonus += 2.0 / float64(latency)
			}
		}

		// Compute deployment cost.
		totalCost := float64(count * deploymentCost)
		// Overall utility for this subset.
		utility := float64(subsetCapacity) + connectivityBonus - totalCost

		if utility > maxUtility {
			maxUtility = utility
		}
	}
	return maxUtility
}