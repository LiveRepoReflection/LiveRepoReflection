package distributed_kmeans

import (
    "math"
    "math/rand"
    "sync"
)

type clusterStats struct {
    sum     []float64
    count   int
}

func euclideanDistance(a, b []float64) float64 {
    sum := 0.0
    for i := range a {
        diff := a[i] - b[i]
        sum += diff * diff
    }
    return math.Sqrt(sum)
}

func findNearestCentroid(point []float64, centroids [][]float64) int {
    minDist := math.MaxFloat64
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

func DistributedKMeans(numWorkers, k int, dataPoints, initialCentroids [][]float64, maxIterations int, threshold float64) [][]float64 {
    centroids := make([][]float64, len(initialCentroids))
    for i := range initialCentroids {
        centroids[i] = make([]float64, len(initialCentroids[i]))
        copy(centroids[i], initialCentroids[i])
    }

    for iter := 0; iter < maxIterations; iter++ {
        var wg sync.WaitGroup
        statsChan := make(chan map[int]clusterStats, numWorkers)

        // Split data among workers
        chunkSize := (len(dataPoints) + numWorkers - 1) / numWorkers

        for w := 0; w < numWorkers; w++ {
            start := w * chunkSize
            end := start + chunkSize
            if end > len(dataPoints) {
                end = len(dataPoints)
            }
            if start >= end {
                continue
            }

            wg.Add(1)
            go func(chunk [][]float64) {
                defer wg.Done()
                localStats := make(map[int]clusterStats)

                for _, point := range chunk {
                    cluster := findNearestCentroid(point, centroids)
                    stat, exists := localStats[cluster]
                    if !exists {
                        stat = clusterStats{
                            sum:   make([]float64, len(point)),
                            count: 0,
                        }
                    }

                    for i := range point {
                        stat.sum[i] += point[i]
                    }
                    stat.count++
                    localStats[cluster] = stat
                }

                statsChan <- localStats
            }(dataPoints[start:end])
        }

        go func() {
            wg.Wait()
            close(statsChan)
        }()

        // Aggregate results from workers
        newCentroids := make([][]float64, k)
        counts := make([]int, k)
        for i := range newCentroids {
            newCentroids[i] = make([]float64, len(centroids[0]))
        }

        for stats := range statsChan {
            for cluster, stat := range stats {
                for i := range stat.sum {
                    newCentroids[cluster][i] += stat.sum[i]
                }
                counts[cluster] += stat.count
            }
        }

        // Handle empty clusters
        for cluster := 0; cluster < k; cluster++ {
            if counts[cluster] == 0 {
                // Reinitialize to random point
                randomIndex := rand.Intn(len(dataPoints))
                copy(newCentroids[cluster], dataPoints[randomIndex])
                continue
            }

            for i := range newCentroids[cluster] {
                newCentroids[cluster][i] /= float64(counts[cluster])
            }
        }

        // Check convergence
        maxChange := 0.0
        for i := range centroids {
            change := euclideanDistance(centroids[i], newCentroids[i])
            if change > maxChange {
                maxChange = change
            }
        }

        centroids = newCentroids
        if maxChange < threshold {
            break
        }
    }

    return centroids
}