package resilient_deploy

import (
	"sort"
)

// DeployResilientService partitions the network nodes into K clusters
// and assigns service replicas based on available resources and connectivity constraints.
// If no valid deployment is possible, it returns an empty slice.
func DeployResilientService(
	N int,
	K int,
	nodes [][]int,
	edges [][]int,
	serviceCPU int,
	serviceRAM int,
	minReplicasPerCluster int,
	minClusterBandwidth int,
	maxClusterLatency int,
	minTotalReplicas int,
) [][]int {

	// Build a qualified connection matrix.
	// qualified[i][j] is true if there is an edge between i and j such that:
	// edge_bandwidth >= minClusterBandwidth and edge_latency <= maxClusterLatency.
	qualified := make([][]bool, N)
	for i := 0; i < N; i++ {
		qualified[i] = make([]bool, N)
	}
	// Initialize self connections as true.
	for i := 0; i < N; i++ {
		qualified[i][i] = true
	}

	// Fill in direct connections from edges.
	// There might be multiple edges between pair; we accept if at least one qualifies.
	for _, edge := range edges {
		u := edge[0]
		v := edge[1]
		bw := edge[2]
		lat := edge[3]
		if bw >= minClusterBandwidth && lat <= maxClusterLatency {
			qualified[u][v] = true
			qualified[v][u] = true
		}
	}

	// A helper function to check if a set of nodes is a clique in the qualified graph.
	isClique := func(group []int) bool {
		for i := 0; i < len(group); i++ {
			for j := i + 1; j < len(group); j++ {
				if !qualified[group[i]][group[j]] {
					return false
				}
			}
		}
		return true
	}

	// Greedy partitioning: go in order 0..N-1 and insert node into an existing cluster if possible.
	clusters := [][]int{}
	for i := 0; i < N; i++ {
		placed := false
		for j := range clusters {
			// Check if adding node i preserves clique property.
			valid := true
			for _, node := range clusters[j] {
				if !qualified[i][node] {
					valid = false
					break
				}
			}
			if valid {
				clusters[j] = append(clusters[j], i)
				placed = true
				break
			}
		}
		if !placed {
			clusters = append(clusters, []int{i})
		}
	}

	// Try to merge clusters if there are more than K clusters.
	mergeHappened := true
	for len(clusters) > K && mergeHappened {
		mergeHappened = false
		nc := len(clusters)
		merged := false
		for i := 0; i < nc && !merged; i++ {
			for j := i + 1; j < nc && !merged; j++ {
				// Check if merging clusters[i] and clusters[j] forms a clique.
				combined := append([]int{}, clusters[i]...)
				combined = append(combined, clusters[j]...)
				if isClique(combined) {
					// Merge clusters[i] and clusters[j]
					clusters[i] = combined
					// Remove clusters[j]
					clusters = append(clusters[:j], clusters[j+1:]...)
					mergeHappened = true
					merged = true
				}
			}
		}
	}

	// If there are fewer clusters than K, try to split clusters.
	// Since any subset of a clique is also a clique, we can always take one node out.
	for len(clusters) < K {
		splitOccurred := false
		for i := 0; i < len(clusters); i++ {
			if len(clusters[i]) > 1 {
				// Remove the last node and form a new cluster.
				newCluster := []int{clusters[i][len(clusters[i])-1]}
				clusters[i] = clusters[i][:len(clusters[i])-1]
				clusters = append(clusters, newCluster)
				splitOccurred = true
				break
			}
		}
		// If no split is possible, break.
		if !splitOccurred {
			break
		}
	}
	// Final check for number of clusters.
	if len(clusters) != K {
		return [][]int{}
	}

	// Check resource constraints on each cluster.
	// A node can host a replica if its CPU and RAM satisfy service requirements.
	nodeCanHost := make([]bool, N)
	for i := 0; i < N; i++ {
		if nodes[i][0] >= serviceCPU && nodes[i][1] >= serviceRAM {
			nodeCanHost[i] = true
		} else {
			nodeCanHost[i] = false
		}
	}

	totalReplicas := 0
	for _, cluster := range clusters {
		validCount := 0
		for _, node := range cluster {
			if nodeCanHost[node] {
				validCount++
			}
		}
		// Each cluster must have at least minReplicasPerCluster replicas.
		if validCount < minReplicasPerCluster {
			return [][]int{}
		}
		totalReplicas += validCount
	}

	if totalReplicas < minTotalReplicas {
		return [][]int{}
	}

	// Resilience requirement:
	// There must exist at least one cluster that remains operational (i.e. with at least minReplicasPerCluster replicas)
	// even after removal of any single node.
	// For each cluster, if the count of valid nodes is at least (minReplicasPerCluster + 1), then that cluster is resilient.
	resilientExists := false
	for _, cluster := range clusters {
		validCount := 0
		for _, node := range cluster {
			if nodeCanHost[node] {
				validCount++
			}
		}
		if validCount >= minReplicasPerCluster+1 {
			resilientExists = true
			break
		}
	}
	if !resilientExists {
		return [][]int{}
	}

	// For consistency, sort each cluster's node IDs.
	for i := range clusters {
		sort.Ints(clusters[i])
	}

	// Also sort the list of clusters by first element.
	sort.Slice(clusters, func(i, j int) bool {
		return clusters[i][0] < clusters[j][0]
	})

	return clusters
}