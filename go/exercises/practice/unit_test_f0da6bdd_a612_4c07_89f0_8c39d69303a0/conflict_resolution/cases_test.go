package conflictresolution

var testCases = []struct {
    description   string
    transactions  []Transaction
    numNodes      int
    expected      map[int]map[string]string
}{
    {
        description: "single transaction, single node",
        transactions: []Transaction{
            {
                ID: 1,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "10", OpType: "WRITE"},
                },
            },
        },
        numNodes: 1,
        expected: map[int]map[string]string{
            0: {"x": "10"},
        },
    },
    {
        description: "two conflicting transactions on same node",
        transactions: []Transaction{
            {
                ID: 2,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "20", OpType: "WRITE"},
                },
            },
            {
                ID: 1,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "10", OpType: "WRITE"},
                },
            },
        },
        numNodes: 1,
        expected: map[int]map[string]string{
            0: {"x": "10"},
        },
    },
    {
        description: "multiple nodes, multiple transactions, no conflicts",
        transactions: []Transaction{
            {
                ID: 1,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "10", OpType: "WRITE"},
                },
            },
            {
                ID: 2,
                Operations: []Operation{
                    {NodeID: 1, Key: "y", Value: "20", OpType: "WRITE"},
                },
            },
        },
        numNodes: 2,
        expected: map[int]map[string]string{
            0: {"x": "10"},
            1: {"y": "20"},
        },
    },
    {
        description: "read operations don't cause conflicts",
        transactions: []Transaction{
            {
                ID: 1,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "10", OpType: "WRITE"},
                },
            },
            {
                ID: 2,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "", OpType: "READ"},
                },
            },
        },
        numNodes: 1,
        expected: map[int]map[string]string{
            0: {"x": "10"},
        },
    },
    {
        description: "complex scenario with multiple conflicts",
        transactions: []Transaction{
            {
                ID: 3,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "30", OpType: "WRITE"},
                    {NodeID: 1, Key: "y", Value: "30", OpType: "WRITE"},
                },
            },
            {
                ID: 1,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "10", OpType: "WRITE"},
                    {NodeID: 1, Key: "y", Value: "10", OpType: "WRITE"},
                },
            },
            {
                ID: 2,
                Operations: []Operation{
                    {NodeID: 0, Key: "x", Value: "20", OpType: "WRITE"},
                    {NodeID: 1, Key: "z", Value: "20", OpType: "WRITE"},
                },
            },
        },
        numNodes: 2,
        expected: map[int]map[string]string{
            0: {"x": "10"},
            1: {"y": "10", "z": "20"},
        },
    },
}