package distributed_kmeans

type Worker struct {
    id      int
    data    [][]float64
    centroids [][]float64
}

func (w *Worker) Process() map[int]clusterStats {
    localStats := make(map[int]clusterStats)

    for _, point := range w.data {
        cluster := findNearestCentroid(point, w.centroids)
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

    return localStats
}