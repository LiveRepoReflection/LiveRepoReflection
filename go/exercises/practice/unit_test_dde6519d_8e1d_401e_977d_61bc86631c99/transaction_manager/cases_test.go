package transaction_manager

// TestCase defines a test case for the TransactionManager
type TestCase struct {
	description string
	operations  []Operation
	expected    []string
}

// Operation represents an operation on the TransactionManager
type Operation struct {
	name           string
	transactionID  int
	serviceNode    int
	prepareVotes   map[int]bool
	expectedError  bool
	expectedState  string
	expectedResult string
}

var testCases = []TestCase{
	{
		description: "Simple successful transaction",
		operations: []Operation{
			{"Begin", 1, 0, nil, false, "ACTIVE", ""},
			{"Participate", 1, 101, nil, false, "ACTIVE", ""},
			{"Participate", 1, 102, nil, false, "ACTIVE", ""},
			{"Prepare", 1, 0, map[int]bool{101: true, 102: true}, false, "PREPARED", ""},
			{"Commit", 1, 0, nil, false, "COMMITTED", ""},
			{"GetTransactionState", 1, 0, nil, false, "COMMITTED", "COMMITTED"},
		},
		expected: []string{"COMMITTED"},
	},
	{
		description: "Transaction with abort during prepare",
		operations: []Operation{
			{"Begin", 2, 0, nil, false, "ACTIVE", ""},
			{"Participate", 2, 201, nil, false, "ACTIVE", ""},
			{"Participate", 2, 202, nil, false, "ACTIVE", ""},
			{"Prepare", 2, 0, map[int]bool{201: true, 202: false}, false, "ABORTED", ""},
			{"GetTransactionState", 2, 0, nil, false, "ABORTED", "ABORTED"},
			{"Commit", 2, 0, nil, true, "ABORTED", ""}, // Should error since transaction aborted
		},
		expected: []string{"ABORTED"},
	},
	{
		description: "Manual abort",
		operations: []Operation{
			{"Begin", 3, 0, nil, false, "ACTIVE", ""},
			{"Participate", 3, 301, nil, false, "ACTIVE", ""},
			{"Abort", 3, 0, nil, false, "ABORTED", ""},
			{"GetTransactionState", 3, 0, nil, false, "ABORTED", "ABORTED"},
		},
		expected: []string{"ABORTED"},
	},
	{
		description: "Service node in multiple transactions",
		operations: []Operation{
			{"Begin", 4, 0, nil, false, "ACTIVE", ""},
			{"Participate", 4, 401, nil, false, "ACTIVE", ""},
			{"Begin", 5, 0, nil, false, "ACTIVE", ""},
			{"Participate", 5, 401, nil, true, "ACTIVE", ""}, // Should error
			{"GetTransactionState", 4, 0, nil, false, "ACTIVE", "ACTIVE"},
			{"GetTransactionState", 5, 0, nil, false, "ACTIVE", "ACTIVE"},
		},
		expected: []string{"ACTIVE", "ACTIVE"},
	},
	{
		description: "Commit without prepare",
		operations: []Operation{
			{"Begin", 6, 0, nil, false, "ACTIVE", ""},
			{"Participate", 6, 601, nil, false, "ACTIVE", ""},
			{"Commit", 6, 0, nil, true, "ACTIVE", ""}, // Should error
			{"GetTransactionState", 6, 0, nil, false, "ACTIVE", "ACTIVE"},
		},
		expected: []string{"ACTIVE"},
	},
	{
		description: "Prepare without participants",
		operations: []Operation{
			{"Begin", 7, 0, nil, false, "ACTIVE", ""},
			{"Prepare", 7, 0, nil, true, "ACTIVE", ""}, // Should error
			{"GetTransactionState", 7, 0, nil, false, "ACTIVE", "ACTIVE"},
		},
		expected: []string{"ACTIVE"},
	},
	{
		description: "Begin same transaction twice",
		operations: []Operation{
			{"Begin", 8, 0, nil, false, "ACTIVE", ""},
			{"Begin", 8, 0, nil, true, "ACTIVE", ""}, // Should error
			{"GetTransactionState", 8, 0, nil, false, "ACTIVE", "ACTIVE"},
		},
		expected: []string{"ACTIVE"},
	},
	{
		description: "Operate on non-existent transaction",
		operations: []Operation{
			{"Participate", 9, 901, nil, true, "", ""}, // Should error
			{"Prepare", 9, 0, nil, true, "", ""},       // Should error
			{"Commit", 9, 0, nil, true, "", ""},        // Should error
			{"Abort", 9, 0, nil, true, "", ""},         // Should error
			{"GetTransactionState", 9, 0, nil, true, "", ""}, // Should error
		},
		expected: []string{""},
	},
	{
		description: "Idempotent commit and abort",
		operations: []Operation{
			{"Begin", 10, 0, nil, false, "ACTIVE", ""},
			{"Participate", 10, 1001, nil, false, "ACTIVE", ""},
			{"Prepare", 10, 0, map[int]bool{1001: true}, false, "PREPARED", ""},
			{"Commit", 10, 0, nil, false, "COMMITTED", ""},
			{"Commit", 10, 0, nil, false, "COMMITTED", ""}, // Should not error
			{"Begin", 11, 0, nil, false, "ACTIVE", ""},
			{"Participate", 11, 1101, nil, false, "ACTIVE", ""},
			{"Abort", 11, 0, nil, false, "ABORTED", ""},
			{"Abort", 11, 0, nil, false, "ABORTED", ""}, // Should not error
		},
		expected: []string{"COMMITTED", "ABORTED"},
	},
	{
		description: "Complex scenario with multiple transactions",
		operations: []Operation{
			{"Begin", 12, 0, nil, false, "ACTIVE", ""},
			{"Participate", 12, 1201, nil, false, "ACTIVE", ""},
			{"Participate", 12, 1202, nil, false, "ACTIVE", ""},
			{"Begin", 13, 0, nil, false, "ACTIVE", ""},
			{"Participate", 13, 1301, nil, false, "ACTIVE", ""},
			{"Prepare", 12, 0, map[int]bool{1201: true, 1202: true}, false, "PREPARED", ""},
			{"Commit", 12, 0, nil, false, "COMMITTED", ""},
			{"Prepare", 13, 0, map[int]bool{1301: false}, false, "ABORTED", ""},
			{"GetTransactionState", 12, 0, nil, false, "COMMITTED", "COMMITTED"},
			{"GetTransactionState", 13, 0, nil, false, "ABORTED", "ABORTED"},
			// Service node in completed transaction can join new transaction
			{"Begin", 14, 0, nil, false, "ACTIVE", ""},
			{"Participate", 14, 1201, nil, false, "ACTIVE", ""},
			{"Prepare", 14, 0, map[int]bool{1201: true}, false, "PREPARED", ""},
			{"Commit", 14, 0, nil, false, "COMMITTED", ""},
			{"GetTransactionState", 14, 0, nil, false, "COMMITTED", "COMMITTED"},
		},
		expected: []string{"COMMITTED", "ABORTED", "COMMITTED"},
	},
}