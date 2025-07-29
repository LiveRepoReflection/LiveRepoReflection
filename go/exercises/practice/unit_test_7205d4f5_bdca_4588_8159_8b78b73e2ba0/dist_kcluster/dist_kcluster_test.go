package dist_kcluster

import (
	"math"
	"testing"
)

func TestDistributedKMeans(t *testing.T) {
	tests := []struct {
		name       string
		workerData [][]NodeEmbedding
		k          int
		epsilon    float64
		want       [][]int
		wantErr    bool
	}{
		{
			name: "empty input",
			workerData: [][]NodeEmbedding{
				{},
				{},
			},
			k:       2,
			epsilon: 1e-6,
			wantErr: true,
		},
		{
			name: "single cluster",
			workerData: [][]NodeEmbedding{
				{
					{NodeID: 1, Features: []float64{1.0, 1.0}},
					{NodeID: 2, Features: []float64{1.1, 1.1}},
				},
				{
					{NodeID: 3, Features: []float64{0.9, 0.9}},
				},
			},
			k:       1,
			epsilon: 1e-6,
			want:    [][]int{{1, 2, 3}},
		},
		{
			name: "two clearly separated clusters",
			workerData: [][]NodeEmbedding{
				{
					{NodeID: 1, Features: []float64{1.0, 1.0}},
					{NodeID: 2, Features: []float64{1.1, 1.1}},
				},
				{
					{NodeID: 3, Features: []float64{10.0, 10.0}},
					{NodeID: 4, Features: []float64{10.1, 10.1}},
				},
			},
			k:       2,
			epsilon: 1e-6,
			want:    [][]int{{1, 2}, {3, 4}},
		},
		{
			name: "invalid k value",
			workerData: [][]NodeEmbedding{
				{
					{NodeID: 1, Features: []float64{1.0, 1.0}},
				},
			},
			k:       0,
			epsilon: 1e-6,
			wantErr: true,
		},
		{
			name: "more clusters than nodes",
			workerData: [][]NodeEmbedding{
				{
					{NodeID: 1, Features: []float64{1.0, 1.0}},
				},
			},
			k:       2,
			epsilon: 1e-6,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := DistributedKMeans(tt.workerData, tt.k, tt.epsilon)
			if (err != nil) != tt.wantErr {
				t.Errorf("DistributedKMeans() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr {
				if len(got) != len(tt.want) {
					t.Errorf("DistributedKMeans() got %d clusters, want %d", len(got), len(tt.want))
					return
				}

				// Convert results to a comparable format
				gotMap := make(map[int]int)
				for clusterIdx, cluster := range got {
					for _, nodeID := range cluster {
						gotMap[nodeID] = clusterIdx
					}
				}

				wantMap := make(map[int]int)
				for clusterIdx, cluster := range tt.want {
					for _, nodeID := range cluster {
						wantMap[nodeID] = clusterIdx
					}
				}

				// Check if the clustering is equivalent
				for nodeID, gotCluster := range gotMap {
					if wantCluster, exists := wantMap[nodeID]; exists && gotCluster != wantCluster {
						t.Errorf("Node %d was in cluster %d, expected cluster %d", nodeID, gotCluster, wantCluster)
					}
				}
			}
		})
	}
}

func TestEuclideanDistance(t *testing.T) {
	tests := []struct {
		name     string
		a, b     []float64
		expected float64
	}{
		{
			name:     "same point",
			a:        []float64{1.0, 1.0},
			b:        []float64{1.0, 1.0},
			expected: 0.0,
		},
		{
			name:     "simple distance",
			a:        []float64{0.0, 0.0},
			b:        []float64{3.0, 4.0},
			expected: 5.0,
		},
		{
			name:     "higher dimensions",
			a:        []float64{1.0, 2.0, 3.0},
			b:        []float64{4.0, 5.0, 6.0},
			expected: math.Sqrt(27),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := euclideanDistance(tt.a, tt.b)
			if math.Abs(got-tt.expected) > 1e-9 {
				t.Errorf("euclideanDistance() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestInitializeCentroids(t *testing.T) {
	tests := []struct {
		name       string
		workerData [][]NodeEmbedding
		k          int
		wantLen    int
		wantErr    bool
	}{
		{
			name: "normal case",
			workerData: [][]NodeEmbedding{
				{
					{NodeID: 1, Features: []float64{1.0, 1.0}},
					{NodeID: 2, Features: []float64{2.0, 2.0}},
				},
				{
					{NodeID: 3, Features: []float64{3.0, 3.0}},
				},
			},
			k:       2,
			wantLen: 2,
		},
		{
			name: "k too large",
			workerData: [][]NodeEmbedding{
				{
					{NodeID: 1, Features: []float64{1.0, 1.0}},
				},
			},
			k:       2,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := initializeCentroids(tt.workerData, tt.k)
			if (err != nil) != tt.wantErr {
				t.Errorf("initializeCentroids() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr && len(got) != tt.wantLen {
				t.Errorf("initializeCentroids() got %d centroids, want %d", len(got), tt.wantLen)
			}
		})
	}
}