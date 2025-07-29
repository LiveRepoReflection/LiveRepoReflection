package partition

type testCase struct {
    description           string
    n                    int
    k                    int
    serviceCosts         []int
    edges                [][]int
    maxClusterSize       int
    maxInterClusterLatency int
    expected             int
}

var testCases = []testCase{
    {
        description: "single node, single cluster",
        n: 1,
        k: 1,
        serviceCosts: []int{5},
        edges: [][]int{},
        maxClusterSize: 1,
        maxInterClusterLatency: 100,
        expected: 5,
    },
    {
        description: "two nodes, two clusters, no edges",
        n: 2,
        k: 2,
        serviceCosts: []int{3, 4},
        edges: [][]int{},
        maxClusterSize: 1,
        maxInterClusterLatency: 100,
        expected: 7,
    },
    {
        description: "three nodes, two clusters with edge constraint",
        n: 3,
        k: 2,
        serviceCosts: []int{1, 2, 3},
        edges: [][]int{{0, 1, 10}, {1, 2, 20}},
        maxClusterSize: 2,
        maxInterClusterLatency: 15,
        expected: 6,
    },
    {
        description: "impossible due to cluster size constraint",
        n: 3,
        k: 2,
        serviceCosts: []int{1, 2, 3},
        edges: [][]int{{0, 1, 10}, {1, 2, 20}},
        maxClusterSize: 1,
        maxInterClusterLatency: 100,
        expected: -1,
    },
    {
        description: "impossible due to latency constraint",
        n: 3,
        k: 2,
        serviceCosts: []int{1, 2, 3},
        edges: [][]int{{0, 1, 10}, {1, 2, 20}},
        maxClusterSize: 2,
        maxInterClusterLatency: 5,
        expected: -1,
    },
    {
        description: "complex case with multiple valid solutions",
        n: 4,
        k: 2,
        serviceCosts: []int{5, 4, 3, 2},
        edges: [][]int{{0, 1, 10}, {1, 2, 20}, {2, 3, 15}, {0, 3, 25}},
        maxClusterSize: 3,
        maxInterClusterLatency: 30,
        expected: 14,
    },
}