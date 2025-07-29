package multiflow

var testCases = []struct {
    description string
    n          int
    edges      [][3]int
    commodities [][3]int
    expected   []int
}{
    {
        description: "basic test case",
        n:          4,
        edges: [][3]int{
            {0, 1, 10},
            {0, 2, 5},
            {1, 2, 15},
            {1, 3, 10},
            {2, 3, 20},
        },
        commodities: [][3]int{
            {0, 3, 5},
            {1, 2, 8},
        },
        expected: []int{5, 8},
    },
    {
        description: "no path between source and sink",
        n:          3,
        edges: [][3]int{
            {0, 1, 10},
        },
        commodities: [][3]int{
            {0, 2, 5},
        },
        expected: []int{0},
    },
    {
        description: "demand exceeds capacity",
        n:          3,
        edges: [][3]int{
            {0, 1, 5},
            {1, 2, 5},
        },
        commodities: [][3]int{
            {0, 2, 10},
        },
        expected: []int{5},
    },
    {
        description: "multiple paths",
        n:          4,
        edges: [][3]int{
            {0, 1, 10},
            {0, 2, 10},
            {1, 3, 10},
            {2, 3, 10},
        },
        commodities: [][3]int{
            {0, 3, 15},
        },
        expected: []int{15},
    },
    {
        description: "cycle in graph",
        n:          4,
        edges: [][3]int{
            {0, 1, 10},
            {1, 2, 10},
            {2, 1, 10},
            {1, 3, 10},
        },
        commodities: [][3]int{
            {0, 3, 10},
        },
        expected: []int{10},
    },
    {
        description: "multiple commodities sharing edges",
        n:          5,
        edges: [][3]int{
            {0, 1, 10},
            {1, 2, 15},
            {2, 3, 10},
            {3, 4, 10},
            {0, 4, 5},
        },
        commodities: [][3]int{
            {0, 4, 8},
            {1, 3, 7},
        },
        expected: []int{8, 7},
    },
}