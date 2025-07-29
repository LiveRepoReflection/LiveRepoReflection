package distributed_kmeans

import (
    "math"
    "testing"
)

func floatSlicesEqual(a, b [][]float64, threshold float64) bool {
    if len(a) != len(b) {
        return false
    }
    for i := range a {
        if len(a[i]) != len(b[i]) {
            return false
        }
        for j := range a[i] {
            if math.Abs(a[i][j]-b[i][j]) > threshold {
                return false
            }
        }
    }
    return true
}

func TestDistributedKMeans(t *testing.T) {
    for _, tc := range testCases {
        result := DistributedKMeans(tc.numWorkers, tc.k, tc.dataPoints, tc.initialCentroids, tc.maxIterations, tc.threshold)
        if !floatSlicesEqual(result, tc.expected, tc.threshold) {
            t.Errorf("DistributedKMeans(%d, %d, %v, %v, %d, %f) = %v, want %v",
                tc.numWorkers, tc.k, tc.dataPoints, tc.initialCentroids, tc.maxIterations, tc.threshold, result, tc.expected)
        }
    }
}

func TestEmptyClusterHandling(t *testing.T) {
    testCase := testCase{
        numWorkers: 2,
        k:          3,
        dataPoints: [][]float64{
            {1.0, 1.0},
            {1.1, 1.1},
            {1.2, 1.2},
        },
        initialCentroids: [][]float64{
            {1.0, 1.0},
            {100.0, 100.0},
            {200.0, 200.0},
        },
        maxIterations: 100,
        threshold:    0.0001,
    }
    
    result := DistributedKMeans(testCase.numWorkers, testCase.k, testCase.dataPoints, testCase.initialCentroids, testCase.maxIterations, testCase.threshold)
    
    // We can't predict exact centroids due to random reinitialization, but verify we have 3 centroids
    if len(result) != testCase.k {
        t.Errorf("Expected %d centroids, got %d", testCase.k, len(result))
    }
}

func BenchmarkDistributedKMeans(b *testing.B) {
    tc := testCases[0]
    for i := 0; i < b.N; i++ {
        DistributedKMeans(tc.numWorkers, tc.k, tc.dataPoints, tc.initialCentroids, tc.maxIterations, tc.threshold)
    }
}