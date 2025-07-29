package resilient_deploy

import (
	"reflect"
	"sort"
	"testing"
)

// Test case structure defining inputs and expected validity.
type testCase struct {
	description             string
	N                       int
	K                       int
	nodes                   [][]int
	edges                   [][]int
	serviceCPU              int
	serviceRAM              int
	minReplicasPerCluster   int
	minClusterBandwidth     int
	maxClusterLatency       int
	minTotalReplicas        int
	expectValid             bool
}

// Helper function to collect and sort all node IDs from the clusters.
func collectNodes(clusters [][]int) []int {
	nodeSet := make(map[int]bool)
	for _, cluster := range clusters {
		for _, node := range cluster {
			nodeSet[node] = true
		}
	}
	var allNodes []int
	for node := range nodeSet {
		allNodes = append(allNodes, node)
	}
	sort.Ints(allNodes)
	return allNodes
}

// Helper function to check if all nodes from 0 to N-1 are present exactly once.
func validateClusterPartition(clusters [][]int, N int) bool {
	// Check if number of clusters is K and union equals all nodes 0...N-1.
	allNodes := collectNodes(clusters)
	if len(allNodes) != N {
		return false
	}
	for i := 0; i < N; i++ {
		if allNodes[i] != i {
			return false
		}
	}
	// Ensure no node appears in more than one cluster.
	appearance := make(map[int]int)
	for _, cluster := range clusters {
		for _, node := range cluster {
			appearance[node]++
			if appearance[node] > 1 {
				return false
			}
		}
	}
	return true
}

func TestDeployResilientService(t *testing.T) {
	testCases := []testCase{
		{
			description:           "Simple valid partition with complete graph",
			N:                     4,
			K:                     2,
			nodes:                 [][]int{{10, 10}, {10, 10}, {10, 10}, {10, 10}},
			edges:                 [][]int{{0, 1, 100, 10}, {0, 2, 100, 10}, {0, 3, 100, 10}, {1, 2, 100, 10}, {1, 3, 100, 10}, {2, 3, 100, 10}},
			serviceCPU:            5,
			serviceRAM:            5,
			minReplicasPerCluster: 1,
			minClusterBandwidth:   50,
			maxClusterLatency:     50,
			minTotalReplicas:      2,
			expectValid:           true,
		},
		{
			description:           "Insufficient resources to deploy service on any node",
			N:                     3,
			K:                     2,
			nodes:                 [][]int{{3, 3}, {3, 3}, {3, 3}},
			edges:                 [][]int{{0, 1, 100, 10}, {1, 2, 100, 10}},
			serviceCPU:            5,
			serviceRAM:            5,
			minReplicasPerCluster: 1,
			minClusterBandwidth:   50,
			maxClusterLatency:     50,
			minTotalReplicas:      2,
			expectValid:           false,
		},
		{
			description:           "Disconnected graph fails bandwidth and connectivity constraints",
			N:                     4,
			K:                     2,
			nodes:                 [][]int{{10, 10}, {10, 10}, {10, 10}, {10, 10}},
			edges:                 [][]int{{0, 1, 100, 10}}, // nodes 2 and 3 are disconnected
			serviceCPU:            5,
			serviceRAM:            5,
			minReplicasPerCluster: 1,
			minClusterBandwidth:   50,
			maxClusterLatency:     50,
			minTotalReplicas:      2,
			expectValid:           false,
		},
		{
			description:           "Valid partition with multiple clusters and minimal connectivity",
			N:                     6,
			K:                     3,
			nodes:                 [][]int{{10, 10}, {10, 10}, {10, 10}, {10, 10}, {10, 10}, {10, 10}},
			edges:                 [][]int{{0, 1, 60, 20}, {2, 3, 60, 20}, {4, 5, 60, 20}},
			serviceCPU:            5,
			serviceRAM:            5,
			minReplicasPerCluster: 1,
			minClusterBandwidth:   50,
			maxClusterLatency:     50,
			minTotalReplicas:      3,
			expectValid:           true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Call the function under test.
			clusters := DeployResilientService(
				tc.N,
				tc.K,
				tc.nodes,
				tc.edges,
				tc.serviceCPU,
				tc.serviceRAM,
				tc.minReplicasPerCluster,
				tc.minClusterBandwidth,
				tc.maxClusterLatency,
				tc.minTotalReplicas,
			)

			// Check validity against expected outcome.
			if !tc.expectValid {
				if len(clusters) != 0 {
					t.Fatalf("Expected an empty result for invalid configuration, got: %v", clusters)
				}
				return
			}

			// For a valid configuration, ensure clusters are returned.
			if len(clusters) != tc.K {
				t.Fatalf("Expected %d clusters, got %d", tc.K, len(clusters))
			}

			// Validate that every node from 0 to N-1 appears exactly once.
			if !validateClusterPartition(clusters, tc.N) {
				t.Fatalf("Clusters partition validation failed. Clusters: %v", clusters)
			}

			// Additional check: ensure total replicas allocated satisfy minimum requirement.
			// Since each node is assumed to host one replica (or a representation of capacity), 
			// total replicas are represented by the total number of nodes allocated.
			totalReplicas := 0
			for _, cluster := range clusters {
				// Assuming a node in a valid cluster can host at least one replica if resources allow.
				// For the purpose of this test, count one replica per node.
				totalReplicas += len(cluster)
				// Also check that each cluster meets the per-cluster minimum replicas.
				if len(cluster) < tc.minReplicasPerCluster {
					t.Fatalf("Cluster %v does not meet minimum replicas per cluster requirement. Got %d, expected at least %d",
						cluster, len(cluster), tc.minReplicasPerCluster)
				}
			}
			if totalReplicas < tc.minTotalReplicas {
				t.Fatalf("Total replicas %d do not meet the minimum total requirement of %d", totalReplicas, tc.minTotalReplicas)
			}

			// As the function may yield multiple valid solutions, we check overall partition properties.
			// Sort each cluster for consistency before comparing.
			for i := range clusters {
				sort.Ints(clusters[i])
			}
			// Flatten clusters into a sorted slice.
			flattened := collectNodes(clusters)
			expected := make([]int, tc.N)
			for i := 0; i < tc.N; i++ {
				expected[i] = i
			}
			if !reflect.DeepEqual(flattened, expected) {
				t.Fatalf("Clusters do not cover all nodes. Got %v, expected %v", flattened, expected)
			}
		})
	}
}