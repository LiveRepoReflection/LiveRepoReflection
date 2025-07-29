package networkflow

var testCases = []struct {
    description    string
    n             int
    capacities    [][]int
    nodeCapacities []int
    requests      [][]int
    expected      int
}{
    {
        description: "simple three node network",
        n:           3,
        capacities: [][]int{
            {0, 5, 0},
            {5, 0, 5},
            {0, 5, 0},
        },
        nodeCapacities: []int{10, 10, 10},
        requests: [][]int{
            {0, 2, 3},
            {0, 2, 2},
            {1, 2, 4},
        },
        expected: 2,
    },
    {
        description: "single node network",
        n:           1,
        capacities:  [][]int{{0}},
        nodeCapacities: []int{5},
        requests:    [][]int{},
        expected:    0,
    },
    {
        description: "disconnected network",
        n:           4,
        capacities: [][]int{
            {0, 5, 0, 0},
            {5, 0, 0, 0},
            {0, 0, 0, 5},
            {0, 0, 5, 0},
        },
        nodeCapacities: []int{10, 10, 10, 10},
        requests: [][]int{
            {0, 2, 3},
            {1, 3, 4},
        },
        expected: 0,
    },
    {
        description: "network with multiple paths",
        n:           4,
        capacities: [][]int{
            {0, 5, 5, 0},
            {5, 0, 5, 5},
            {5, 5, 0, 5},
            {0, 5, 5, 0},
        },
        nodeCapacities: []int{10, 10, 10, 10},
        requests: [][]int{
            {0, 3, 3},
            {0, 3, 4},
            {1, 2, 2},
        },
        expected: 3,
    },
    {
        description: "network with node capacity constraints",
        n:           3,
        capacities: [][]int{
            {0, 10, 0},
            {10, 0, 10},
            {0, 10, 0},
        },
        nodeCapacities: []int{5, 3, 5},
        requests: [][]int{
            {0, 2, 2},
            {0, 2, 2},
            {0, 2, 2},
        },
        expected: 1,
    },
    {
        description: "duplicate requests",
        n:           2,
        capacities: [][]int{
            {0, 5},
            {5, 0},
        },
        nodeCapacities: []int{10, 10},
        requests: [][]int{
            {0, 1, 2},
            {0, 1, 2},
            {0, 1, 2},
        },
        expected: 2,
    },
}