package nexus

// TestCase represents a test case for k-core decomposition
type testCase struct {
    description string
    network     []string
    k          int
    expected   []int
    expectErr  bool
}

// Basic test cases for the k-core decomposition algorithm
var kCoreTestCases = []testCase{
    {
        description: "Basic graph with k=2",
        network: []string{
            "1:2,3,4",
            "2:1,3,5",
            "3:1,2,4,6",
            "4:1,3,6",
            "5:2",
            "6:3,4,7",
            "7:6",
        },
        k: 2,
        expected: []int{1, 2, 3, 4, 6},
        expectErr: false,
    },
    {
        description: "Empty graph",
        network: []string{},
        k: 1,
        expected: []int{},
        expectErr: false,
    },
    {
        description: "Single node graph",
        network: []string{
            "1:",
        },
        k: 1,
        expected: []int{},
        expectErr: false,
    },
    {
        description: "Complete graph with k=3",
        network: []string{
            "1:2,3,4",
            "2:1,3,4",
            "3:1,2,4",
            "4:1,2,3",
        },
        k: 3,
        expected: []int{1, 2, 3, 4},
        expectErr: false,
    },
    {
        description: "Invalid k value (negative)",
        network: []string{
            "1:2,3",
            "2:1,3",
            "3:1,2",
        },
        k: -1,
        expected: nil,
        expectErr: true,
    },
    {
        description: "Large k value (larger than max degree)",
        network: []string{
            "1:2,3",
            "2:1,3",
            "3:1,2",
        },
        k: 5,
        expected: []int{},
        expectErr: false,
    },
}