package dist_kcluster

import (
	"errors"
	"math"
	"math/rand"
	"time"
)

type NodeEmbedding struct {
	NodeID   int
	Features []float64
}

func DistributedKMeans(workerData [][]NodeEmbedding, k int, epsilon float64) ([][]int, error) {
	if k <= 0 {
		return nil, errors.New("k must be positive")
	}

	// Flatten worker data to count total nodes
	totalNodes := 0
	for _, worker := range workerData {
		totalNodes += len(worker)
	}
	if totalNodes == 0 {
		return nil, errors.New("no data to cluster")
	}
	if k > totalNodes {
		return nil, errors.New("k cannot be larger than number of nodes")
	}

	// Initialize centroids
	centroids, err := initializeCentroids(workerData, k)
	if err != nil {
		return nil, err
	}

	// Initialize random number generator
	rand.Seed(time.Now().UnixNano())

	for {
		// Initialize variables for aggregation
		sums := make([][]float64, k)
		counts := make([]int, k)
		for i := range sums {
			sums[i] = make([]float64, len(workerData[0][0].Features))
		}

		// Assign nodes to nearest centroids and collect sums
		for _, worker := range workerData {
			for _, node := range worker {
				nearestIdx := findNearestCentroid(node.Features, centroids)
				for i := range node.Features {
					sums[nearestIdx][i] += node.Features[i]
				}
				counts[nearestIdx]++
			}
		}

		// Calculate new centroids and track movement
		maxMovement := 0.0
		newCentroids := make([][]float64, k)
		for i := range newCentroids {
			newCentroids[i] = make([]float64, len(centroids[i]))
			if counts[i] > 0 {
				for j := range centroids[i] {
					newCentroids[i][j] = sums[i][j] / float64(counts[i])
				}
				maxMovement = math.Max(maxMovement, euclideanDistance(centroids[i], newCentroids[i]))
			}
		}

		// Check for convergence
		if maxMovement < epsilon {
			break
		}
		centroids = newCentroids
	}

	// Final assignment of nodes to clusters
	clusters := make([][]int, k)
	for _, worker := range workerData {
		for _, node := range worker {
			nearestIdx := findNearestCentroid(node.Features, centroids)
			clusters[nearestIdx] = append(clusters[nearestIdx], node.NodeID)
		}
	}

	return clusters, nil
}

func initializeCentroids(workerData [][]NodeEmbedding, k int) ([][]float64, error) {
	// Flatten all nodes
	var allNodes []NodeEmbedding
	for _, worker := range workerData {
		allNodes = append(allNodes, worker...)
	}

	if len(allNodes) < k {
		return nil, errors.New("not enough nodes for k clusters")
	}

	// K-Means++ initialization
	centroids := make([][]float64, k)
	centroids[0] = make([]float64, len(allNodes[0].Features))
	copy(centroids[0], allNodes[rand.Intn(len(allNodes))].Features)

	for i := 1; i < k; i++ {
		// Calculate distances to nearest centroid for each point
		distances := make([]float64, len(allNodes))
		total := 0.0
		for j, node := range allNodes {
			minDist := math.MaxFloat64
			for c := 0; c < i; c++ {
				dist := euclideanDistance(node.Features, centroids[c])
				if dist < minDist {
					minDist = dist
				}
			}
			distances[j] = minDist * minDist
			total += distances[j]
		}

		// Select next centroid with probability proportional to distance squared
		r := rand.Float64() * total
		sum := 0.0
		for j, d := range distances {
			sum += d
			if sum >= r {
				centroids[i] = make([]float64, len(allNodes[j].Features))
				copy(centroids[i], allNodes[j].Features)
				break
			}
		}
	}

	return centroids, nil
}

func findNearestCentroid(features []float64, centroids [][]float64) int {
	minDist := math.MaxFloat64
	nearestIdx := 0

	for i, centroid := range centroids {
		dist := euclideanDistance(features, centroid)
		if dist < minDist {
			minDist = dist
			nearestIdx = i
		}
	}

	return nearestIdx
}

func euclideanDistance(a, b []float64) float64 {
	sum := 0.0
	for i := range a {
		diff := a[i] - b[i]
		sum += diff * diff
	}
	return math.Sqrt(sum)
}