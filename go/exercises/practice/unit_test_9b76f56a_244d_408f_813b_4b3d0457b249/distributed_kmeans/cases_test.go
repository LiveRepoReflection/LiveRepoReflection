package distributed_kmeans

type testCase struct {
    numWorkers      int
    k               int
    dataPoints      [][]float64
    initialCentroids [][]float64
    expected        [][]float64
    maxIterations   int
    threshold       float64
}

var testCases = []testCase{
    {
        numWorkers: 2,
        k:          2,
        dataPoints: [][]float64{
            {1.0, 1.0},
            {1.1, 1.1},
            {4.0, 4.0},
            {4.1, 4.1},
        },
        initialCentroids: [][]float64{
            {1.0, 1.0},
            {4.0, 4.0},
        },
        expected: [][]float64{
            {1.05, 1.05},
            {4.05, 4.05},
        },
        maxIterations: 100,
        threshold:    0.0001,
    },
    {
        numWorkers: 3,
        k:          3,
        dataPoints: [][]float64{
            {1.0, 2.0},
            {1.0, 2.1},
            {5.0, 8.0},
            {5.1, 8.0},
            {10.0, 2.0},
            {10.0, 2.1},
        },
        initialCentroids: [][]float64{
            {1.0, 2.0},
            {5.0, 8.0},
            {10.0, 2.0},
        },
        expected: [][]float64{
            {1.0, 2.05},
            {5.05, 8.0},
            {10.0, 2.05},
        },
        maxIterations: 100,
        threshold:    0.0001,
    },
    {
        numWorkers: 1,
        k:          1,
        dataPoints: [][]float64{
            {1.0, 1.0},
            {1.1, 1.1},
            {1.2, 1.2},
        },
        initialCentroids: [][]float64{
            {1.0, 1.0},
        },
        expected: [][]float64{
            {1.1, 1.1},
        },
        maxIterations: 100,
        threshold:    0.0001,
    },
}