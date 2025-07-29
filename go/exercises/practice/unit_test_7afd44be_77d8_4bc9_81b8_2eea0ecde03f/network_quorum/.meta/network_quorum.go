package network_quorum

func MinimumTotalReplicas(n int, m int, k int) int {
	replicasPerItem := 2*k - 1
	return m * replicasPerItem
}