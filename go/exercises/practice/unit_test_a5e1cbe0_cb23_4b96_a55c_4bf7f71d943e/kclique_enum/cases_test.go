package kclique

// Test cases for k-clique enumeration
var testCases = []struct {
    description string
    n          int
    k          int
    adjList    map[int][]int
    expected   [][]int
}{
    {
        description: "small graph with one 3-clique",
        n:          3,
        k:          3,
        adjList: map[int][]int{
            0: {1, 2},
            1: {0, 2},
            2: {0, 1},
        },
        expected: [][]int{{0, 1, 2}},
    },
    {
        description: "graph with multiple 3-cliques",
        n:          5,
        k:          3,
        adjList: map[int][]int{
            0: {1, 2, 3},
            1: {0, 2, 3},
            2: {0, 1, 3},
            3: {0, 1, 2, 4},
            4: {3},
        },
        expected: [][]int{
            {0, 1, 2},
            {0, 1, 3},
            {0, 2, 3},
            {1, 2, 3},
        },
    },
    {
        description: "graph with no k-cliques",
        n:          4,
        k:          3,
        adjList: map[int][]int{
            0: {1},
            1: {0, 2},
            2: {1, 3},
            3: {2},
        },
        expected: [][]int{},
    },
    {
        description: "complete graph k=2",
        n:          3,
        k:          2,
        adjList: map[int][]int{
            0: {1, 2},
            1: {0, 2},
            2: {0, 1},
        },
        expected: [][]int{
            {0, 1},
            {0, 2},
            {1, 2},
        },
    },
    {
        description: "single vertex k=1",
        n:          1,
        k:          1,
        adjList: map[int][]int{
            0: {},
        },
        expected: [][]int{{0}},
    },
}