package network_deploy

func OptimizeDeployment(N int, M int, R []int, C []int, B [][]int, V [][]int, S int, L int, Lxy [][]int, K int) int {
	// Total deployment cost is the sum of individual service costs.
	totalCost := 0
	for _, cost := range C {
		totalCost += cost
	}
	srvCount := len(Lxy)
	assignment := make([]int, N) // assignment[i] = server index for service i

	// Precompute forced pairing matrix:
	// If B[i][j] is 0 and V[i][j] > 0, then services i and j must be deployed on the same server.
	forced := make([][]bool, N)
	for i := 0; i < N; i++ {
		forced[i] = make([]bool, N)
	}
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			if i != j {
				if B[i][j] == 0 && V[i][j] > 0 {
					forced[i][j] = true
				}
			}
		}
	}

	// Variables to keep track of resource usage and service count per server.
	serverRes := make([]int, srvCount)
	serverCount := make([]int, srvCount)

	// found will be set to true if a valid deployment assignment is found.
	found := false

	// backtrack recursively over service assignments.
	var backtrack func(i int)
	backtrack = func(i int) {
		if found {
			return
		}
		if i == N {
			// At a complete assignment, check the redundancy and latency constraints.
			usedServers := make([]int, 0)
			for s := 0; s < srvCount; s++ {
				if serverCount[s] > 0 {
					// Each used server must host at least K services.
					if serverCount[s] < K {
						return
					}
					usedServers = append(usedServers, s)
				}
			}
			// Check latency constraint: For every two distinct used servers, the latency must be <= L.
			for a := 0; a < len(usedServers); a++ {
				for b := a + 1; b < len(usedServers); b++ {
					if Lxy[usedServers[a]][usedServers[b]] > L {
						return
					}
				}
			}
			found = true
			return
		}

		// Try assigning service i to each of the available servers.
		for s := 0; s < srvCount; s++ {
			// Check server resource constraint.
			if serverRes[s]+R[i] > S {
				continue
			}
			// Check communication constraints with previously assigned services.
			valid := true
			for j := 0; j < i; j++ {
				if assignment[j] != s {
					// If i and j are forced to be together but are on different servers.
					if forced[i][j] || forced[j][i] {
						valid = false
						break
					}
					// For services deployed on different servers, ensure communication volume is within the available bandwidth.
					if V[i][j] > B[i][j] {
						valid = false
						break
					}
				}
			}
			if !valid {
				continue
			}

			// Assign service i to server s.
			assignment[i] = s
			serverRes[s] += R[i]
			serverCount[s]++

			backtrack(i + 1)
			if found {
				return
			}

			// Backtrack the assignment.
			serverRes[s] -= R[i]
			serverCount[s]--
		}
	}

	backtrack(0)
	if found {
		return totalCost
	}
	return -1
}