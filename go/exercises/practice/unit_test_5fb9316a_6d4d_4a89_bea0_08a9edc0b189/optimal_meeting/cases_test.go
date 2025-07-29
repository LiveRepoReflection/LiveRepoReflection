package optimal_meeting

var testCases = []struct {
    description     string
    graph          map[int][]Edge
    friendLocations []int
    expected       int
}{
    {
        description: "simple graph with two friends",
        graph: map[int][]Edge{
            1: {{To: 2, Weight: 10}, {To: 3, Weight: 15}},
            2: {{To: 1, Weight: 10}, {To: 4, Weight: 12}},
            3: {{To: 1, Weight: 15}, {To: 4, Weight: 20}},
            4: {{To: 2, Weight: 12}, {To: 3, Weight: 20}},
        },
        friendLocations: []int{1, 4},
        expected:       2,
    },
    {
        description: "empty graph",
        graph:       map[int][]Edge{},
        friendLocations: []int{1},
        expected:       -1,
    },
    {
        description: "empty friend locations",
        graph: map[int][]Edge{
            1: {{To: 2, Weight: 1}},
            2: {{To: 1, Weight: 1}},
        },
        friendLocations: []int{},
        expected:       -1,
    },
    {
        description: "single friend",
        graph: map[int][]Edge{
            1: {{To: 2, Weight: 1}},
            2: {{To: 1, Weight: 1}},
        },
        friendLocations: []int{1},
        expected:       1,
    },
    {
        description: "all friends at same location",
        graph: map[int][]Edge{
            1: {{To: 2, Weight: 1}},
            2: {{To: 1, Weight: 1}, {To: 3, Weight: 1}},
            3: {{To: 2, Weight: 1}},
        },
        friendLocations: []int{2, 2, 2},
        expected:       2,
    },
    {
        description: "disconnected graph",
        graph: map[int][]Edge{
            1: {{To: 2, Weight: 1}},
            2: {{To: 1, Weight: 1}},
            3: {{To: 4, Weight: 1}},
            4: {{To: 3, Weight: 1}},
        },
        friendLocations: []int{1, 3},
        expected:       -1,
    },
    {
        description: "complex graph with multiple friends",
        graph: map[int][]Edge{
            1: {{To: 2, Weight: 5}, {To: 3, Weight: 2}},
            2: {{To: 1, Weight: 5}, {To: 3, Weight: 3}, {To: 4, Weight: 1}},
            3: {{To: 1, Weight: 2}, {To: 2, Weight: 3}, {To: 4, Weight: 6}},
            4: {{To: 2, Weight: 1}, {To: 3, Weight: 6}, {To: 5, Weight: 4}},
            5: {{To: 4, Weight: 4}},
        },
        friendLocations: []int{1, 3, 5},
        expected:       2,
    },
}