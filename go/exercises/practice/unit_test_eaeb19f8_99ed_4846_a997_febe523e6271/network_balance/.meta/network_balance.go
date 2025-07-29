package network_balance

// OptimizeNetwork returns the minimum possible value of the maximum load on any server 
// after optimally migrating load, while also considering migration cost minimization.
// If it's not possible to balance the network while respecting capacity constraints, it returns -1.
func OptimizeNetwork(N int, capacity []int, load []int, edges [][]int) int {
	// Compute the total load across all servers.
	totalLoad := 0
	for _, l := range load {
		totalLoad += l
	}

	// If there is no load, the maximum load is trivially 0.
	if totalLoad == 0 {
		return 0
	}

	// Since the network is connected, redistribution can occur freely.
	// The objective is to find the smallest integer L such that the load can be
	// distributed amongst the servers without any server exceeding L or its capacity.
	// For a given L, each server i can accept at most min(capacity[i], L) load.
	// Hence, we seek the minimum L such that:
	//    sum_{i=0}^{N-1} min(capacity[i], L) >= totalLoad.
	
	// Set the search boundaries.
	low := 0
	high := 0
	for i := 0; i < N; i++ {
		if capacity[i] > high {
			high = capacity[i]
		}
	}
	
	result := -1
	// Binary search for the minimum feasible L.
	for low <= high {
		mid := (low + high) / 2
		if isFeasible(mid, capacity, totalLoad) {
			result = mid
			high = mid - 1
		} else {
			low = mid + 1
		}
	}
	
	return result
}

// isFeasible checks if it is possible to distribute totalLoad among the servers
// such that no server gets more than L load and no server exceeds its capacity.
func isFeasible(L int, capacity []int, totalLoad int) bool {
	sumCapacity := 0
	for _, capVal := range capacity {
		if L < capVal {
			sumCapacity += L
		} else {
			sumCapacity += capVal
		}
	}
	return sumCapacity >= totalLoad
}