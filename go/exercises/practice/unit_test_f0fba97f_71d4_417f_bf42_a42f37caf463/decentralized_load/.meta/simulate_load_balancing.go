package decentralized_load

import (
	"math/rand"
)

func simulate_load_balancing(N int, M int, C []int, batches []int, K int) int {
	// globalLoad tracks the actual load on each server
	globalLoad := make([]int, N)
	// dispatchNodes holds the local view of each dispatch node as float64 slice of length N
	dispatchNodes := make([][]float64, M)
	for j := 0; j < M; j++ {
		dispatchNodes[j] = make([]float64, N)
	}

	maxObserved := 0

	// Process each batch of incoming requests
	for _, batch := range batches {
		// Randomly select a dispatch node
		j := rand.Intn(M)
		remaining := batch

		// Greedy round-robin allocation while respecting local view capacity constraints.
		// It assigns one request at a time to the first available server.
		for remaining > 0 {
			allocatedThisCycle := false
			for i := 0; i < N && remaining > 0; i++ {
				// Calculate available capacity based on local view of dispatch node j.
				available := float64(C[i]) - dispatchNodes[j][i]
				if available >= 1 {
					// Allocate one request
					dispatchNodes[j][i] += 1
					globalLoad[i] += 1
					remaining--
					allocatedThisCycle = true
					if globalLoad[i] > maxObserved {
						maxObserved = globalLoad[i]
					}
				}
			}
			// If no allocation could be made in this cycle, break to avoid infinite loop.
			if !allocatedThisCycle {
				break
			}
		}

		// Gossip Protocol:
		// Each dispatch node randomly selects K other nodes and averages its server load view with each selected node.
		for x := 0; x < M; x++ {
			for k := 0; k < K; k++ {
				var y int
				if M > 1 {
					// Ensure that a node does not gossip with itself.
					for {
						y = rand.Intn(M)
						if y != x {
							break
						}
					}
				} else {
					// If there is only one dispatch node, skip gossip.
					continue
				}
				// Average the local views between dispatch node x and dispatch node y.
				for i := 0; i < N; i++ {
					avg := (dispatchNodes[x][i] + dispatchNodes[y][i]) / 2
					dispatchNodes[x][i] = avg
					dispatchNodes[y][i] = avg
				}
			}
		}
	}

	return maxObserved
}