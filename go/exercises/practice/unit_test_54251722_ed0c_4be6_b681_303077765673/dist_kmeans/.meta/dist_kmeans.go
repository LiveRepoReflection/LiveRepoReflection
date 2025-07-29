package dist_kmeans

import (
	"math"
	"math/rand"
	"sync"
)

type Cluster struct {
	Sum     []float64
	Count   int
	Centroid []float64
}

func NodeCompute(nodeID int, data [][]float64, k int, centroids [][]float64, threshold float64) ([][]float64, []int) {
	clusters := make([]Cluster, k)
	for i := range clusters {
		clusters[i].Sum = make([]float64, len(centroids[0]))
		clusters[i].Centroid = make([]float64, len(centroids[0]))
		copy(clusters[i].Centroid, centroids[i])
	}

	for _, point := range data {
		nearest := findNearestCentroid(point, centroids)
		for d := range point {
			clusters[nearest].Sum[d] += point[d]
		}
		clusters[nearest].Count++
	}

	sums := make([][]float64, k)
	counts := make([]int, k)
	for i := range clusters {
		sums[i] = clusters[i].Sum
		counts[i] = clusters[i].Count
	}

	return sums, counts
}

func CoordinatorAggregate(nodeResults [][][]float64, nodeCounts [][]int, k int, numNodes int, dimensionality int) ([][]float64, float64) {
	newCentroids := make([][]float64, k)
	maxChange := 0.0

	for i := 0; i < k; i++ {
		newCentroids[i] = make([]float64, dimensionality)
		totalCount := 0

		for n := 0; n < numNodes; n++ {
			for d := 0; d < dimensionality; d++ {
				newCentroids[i][d] += nodeResults[n][i][d]
			}
			totalCount += nodeCounts[n][i]
		}

		if totalCount > 0 {
			for d := 0; d < dimensionality; d++ {
				newCentroids[i][d] /= float64(totalCount)
			}
		}
	}

	return newCentroids, maxChange
}

func DistributedKMeans(numNodes int, nodeData [][][]float64, k int, threshold float64, maxIter int) [][]float64 {
	dimensionality := len(nodeData[0][0])
	centroids := initializeCentroids(numNodes, nodeData, k, dimensionality)

	var wg sync.WaitGroup
	resultsChan := make(chan struct {
		sums   [][]float64
		counts []int
	}, numNodes)

	for iter := 0; iter < maxIter; iter++ {
		wg.Add(numNodes)
		for nodeID := 0; nodeID < numNodes; nodeID++ {
			go func(id int) {
				defer wg.Done()
				sums, counts := NodeCompute(id, nodeData[id], k, centroids, threshold)
				resultsChan <- struct {
					sums   [][]float64
					counts []int
				}{sums, counts}
			}(nodeID)
		}

		go func() {
			wg.Wait()
			close(resultsChan)
		}()

		nodeResults := make([][][]float64, numNodes)
		nodeCounts := make([][]int, numNodes)
		i := 0
		for result := range resultsChan {
			nodeResults[i] = result.sums
			nodeCounts[i] = result.counts
			i++
		}

		newCentroids, maxChange := CoordinatorAggregate(nodeResults, nodeCounts, k, numNodes, dimensionality)
		if maxChange < threshold {
			break
		}
		centroids = newCentroids
	}

	return centroids
}

func initializeCentroids(numNodes int, nodeData [][][]float64, k int, dim int) [][]float64 {
	rand.Seed(42)
	centroids := make([][]float64, k)
	
	// K-means++ initialization
	centroids[0] = nodeData[rand.Intn(numNodes)][rand.Intn(len(nodeData[0]))]
	
	for i := 1; i < k; i++ {
		var distances []float64
		var total float64
		
		for _, data := range nodeData {
			for _, point := range data {
				minDist := math.Inf(1)
				for j := 0; j < i; j++ {
					dist := euclideanDistance(point, centroids[j])
					if dist < minDist {
						minDist = dist
					}
				}
				distances = append(distances, minDist)
				total += minDist
			}
		}
		
		r := rand.Float64() * total
		var sum float64
		for _, data := range nodeData {
			for idx, point := range data {
				sum += distances[idx]
				if sum >= r {
					centroids[i] = make([]float64, dim)
					copy(centroids[i], point)
					break
				}
			}
		}
	}
	
	return centroids
}

func findNearestCentroid(point []float64, centroids [][]float64) int {
	minDist := math.Inf(1)
	nearest := 0

	for i, centroid := range centroids {
		dist := euclideanDistance(point, centroid)
		if dist < minDist {
			minDist = dist
			nearest = i
		}
	}

	return nearest
}

func euclideanDistance(a, b []float64) float64 {
	sum := 0.0
	for i := range a {
		diff := a[i] - b[i]
		sum += diff * diff
	}
	return math.Sqrt(sum)
}