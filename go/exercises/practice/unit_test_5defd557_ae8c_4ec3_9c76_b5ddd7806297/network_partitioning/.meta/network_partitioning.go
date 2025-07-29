package network_partitioning

const Weight = 10000

func PartitionNetwork(N int, K int, L []int, C [][]int) []int {
	assignment := make([]int, N)
	partitionLoad := make([]int, K)
	// initial assignment: assign each node to the partition with minimum current load
	for i := 0; i < N; i++ {
		bestPart := 0
		minLoad := partitionLoad[0]
		for p := 1; p < K; p++ {
			if partitionLoad[p] < minLoad {
				bestPart = p
				minLoad = partitionLoad[p]
			}
		}
		assignment[i] = bestPart
		partitionLoad[bestPart] += L[i]
	}

	globalInterCost := calcInterCost(assignment, C)
	imbalance := calcImbalance(partitionLoad)
	globalScore := globalInterCost + Weight*imbalance

	improved := true
	iterations := 0
	// iterative improvement phase
	for improved && iterations < 1000 {
		improved = false
		iterations++
		for i := 0; i < N; i++ {
			currentPart := assignment[i]
			for candidate := 0; candidate < K; candidate++ {
				if candidate == currentPart {
					continue
				}
				// calculate delta in inter-partition communication cost for moving node i
				deltaInter := 0
				for j := 0; j < N; j++ {
					if j == i {
						continue
					}
					if assignment[j] == currentPart {
						// was internal, becomes external
						deltaInter += C[i][j]
					} else if assignment[j] == candidate {
						// was external, becomes internal
						deltaInter -= C[i][j]
					}
				}

				// calculate new imbalance if node i is moved
				newPartitionLoad := make([]int, K)
				copy(newPartitionLoad, partitionLoad)
				newPartitionLoad[currentPart] -= L[i]
				newPartitionLoad[candidate] += L[i]
				newImbalance := calcImbalance(newPartitionLoad)
				deltaImbalance := newImbalance - imbalance

				candidateImprovement := deltaInter + Weight*deltaImbalance

				if candidateImprovement < 0 {
					// commit move
					assignment[i] = candidate
					partitionLoad[currentPart] -= L[i]
					partitionLoad[candidate] += L[i]
					globalScore += candidateImprovement
					imbalance = newImbalance
					improved = true
					// exit inner loops to restart the pass
					goto restartOuter
				}
			}
		}
	restartOuter:
		if improved {
			continue
		}
	}

	_ = globalScore // globalScore is computed for evaluation but not used further
	return assignment
}

func calcInterCost(assignment []int, C [][]int) int {
	interCost := 0
	N := len(assignment)
	for i := 0; i < N; i++ {
		for j := i + 1; j < N; j++ {
			if assignment[i] != assignment[j] {
				interCost += C[i][j]
			}
		}
	}
	return interCost
}

func calcImbalance(partitionLoad []int) int {
	if len(partitionLoad) == 0 {
		return 0
	}
	maxLoad := partitionLoad[0]
	minLoad := partitionLoad[0]
	for _, load := range partitionLoad {
		if load > maxLoad {
			maxLoad = load
		}
		if load < minLoad {
			minLoad = load
		}
	}
	return maxLoad - minLoad
}