package dist_kmeans

import (
	"math/rand"
	"testing"
)

func TestNodeCompute(t *testing.T) {
	tests := []struct {
		name      string
		nodeID    int
		data      [][]float64
		k         int
		centroids [][]float64
		threshold float64
	}{
		{
			name:   "simple 2D clustering",
			nodeID: 0,
			data: [][]float64{
				{1.0, 1.0},
				{1.1, 1.1},
				{5.0, 5.0},
				{5.1, 5.1},
			},
			k: 2,
			centroids: [][]float64{
				{1.0, 1.0},
				{5.0, 5.0},
			},
			threshold: 0.01,
		},
		{
			name:   "single cluster",
			nodeID: 0,
			data: [][]float64{
				{1.0, 1.0},
				{1.1, 1.1},
				{1.2, 1.2},
			},
			k: 1,
			centroids: [][]float64{
				{1.0, 1.0},
			},
			threshold: 0.01,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			sums, counts := NodeCompute(tt.nodeID, tt.data, tt.k, tt.centroids, tt.threshold)
			
			if len(sums) != tt.k {
				t.Errorf("Expected %d cluster sums, got %d", tt.k, len(sums))
			}
			if len(counts) != tt.k {
				t.Errorf("Expected %d cluster counts, got %d", tt.k, len(counts))
			}
		})
	}
}

func TestCoordinatorAggregate(t *testing.T) {
	tests := []struct {
		name         string
		nodeResults  [][][]float64
		nodeCounts   [][]int
		k            int
		numNodes     int
		dimensionality int
	}{
		{
			name: "two nodes two clusters",
			nodeResults: [][][]float64{
				{
					{2.1, 2.1},  // Node 0, Cluster 0 sum
					{10.1, 10.1}, // Node 0, Cluster 1 sum
				},
				{
					{2.2, 2.2},  // Node 1, Cluster 0 sum
					{10.2, 10.2}, // Node 1, Cluster 1 sum
				},
			},
			nodeCounts: [][]int{
				{2, 1}, // Node 0 counts
				{2, 1}, // Node 1 counts
			},
			k:            2,
			numNodes:     2,
			dimensionality: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			newCentroids, maxChange := CoordinatorAggregate(tt.nodeResults, tt.nodeCounts, tt.k, tt.numNodes, tt.dimensionality)
			
			if len(newCentroids) != tt.k {
				t.Errorf("Expected %d centroids, got %d", tt.k, len(newCentroids))
			}
			if maxChange < 0 {
				t.Errorf("Max change should be non-negative, got %f", maxChange)
			}
		})
	}
}

func TestDistributedKMeans(t *testing.T) {
	rand.Seed(42) // For reproducible tests
	
	tests := []struct {
		name       string
		numNodes   int
		data       [][]float64
		k          int
		threshold  float64
		maxIter    int
	}{
		{
			name:      "basic 2D clustering",
			numNodes:  2,
			data:      generateTestData(100, 2),
			k:         3,
			threshold: 0.001,
			maxIter:   100,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Split data across nodes
			nodeData := make([][][]float64, tt.numNodes)
			for i := range nodeData {
				start := i * len(tt.data) / tt.numNodes
				end := (i + 1) * len(tt.data) / tt.numNodes
				nodeData[i] = tt.data[start:end]
			}

			// Run distributed K-Means
			centroids := DistributedKMeans(tt.numNodes, nodeData, tt.k, tt.threshold, tt.maxIter)
			
			if len(centroids) != tt.k {
				t.Errorf("Expected %d centroids, got %d", tt.k, len(centroids))
			}
		})
	}
}

func generateTestData(n, dim int) [][]float64 {
	data := make([][]float64, n)
	for i := range data {
		point := make([]float64, dim)
		for d := range point {
			point[d] = rand.Float64() * 10
		}
		data[i] = point
	}
	return data
}

func BenchmarkDistributedKMeans(b *testing.B) {
	numNodes := 4
	k := 5
	threshold := 0.01
	maxIter := 50
	data := generateTestData(10000, 10)
	
	// Split data across nodes
	nodeData := make([][][]float64, numNodes)
	for i := range nodeData {
		start := i * len(data) / numNodes
		end := (i + 1) * len(data) / numNodes
		nodeData[i] = data[start:end]
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		DistributedKMeans(numNodes, nodeData, k, threshold, maxIter)
	}
}