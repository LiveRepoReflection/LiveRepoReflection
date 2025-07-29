package disttxmanager

// Test cases for the distributed transaction manager
type txTestCase struct {
	description string
	operations  []operation
	expected    []expectedResult
}

type operation struct {
	txID     int
	opType   string // "begin", "get", "set", "commit", "rollback"
	storeID  int
	key      string
	value    string
	expected error
}

type expectedResult struct {
	storeID int
	key     string
	value   string
}

var testCases = []txTestCase{
	{
		description: "basic single transaction",
		operations: []operation{
			{txID: 1, opType: "begin", expected: nil},
			{txID: 1, opType: "set", storeID: 0, key: "key1", value: "value1", expected: nil},
			{txID: 1, opType: "commit", expected: nil},
		},
		expected: []expectedResult{
			{storeID: 0, key: "key1", value: "value1"},
		},
	},
	{
		description: "concurrent transactions",
		operations: []operation{
			{txID: 1, opType: "begin", expected: nil},
			{txID: 2, opType: "begin", expected: nil},
			{txID: 1, opType: "set", storeID: 0, key: "key1", value: "value1", expected: nil},
			{txID: 2, opType: "set", storeID: 1, key: "key2", value: "value2", expected: nil},
			{txID: 1, opType: "commit", expected: nil},
			{txID: 2, opType: "commit", expected: nil},
		},
		expected: []expectedResult{
			{storeID: 0, key: "key1", value: "value1"},
			{storeID: 1, key: "key2", value: "value2"},
		},
	},
	{
		description: "transaction rollback",
		operations: []operation{
			{txID: 1, opType: "begin", expected: nil},
			{txID: 1, opType: "set", storeID: 0, key: "key1", value: "value1", expected: nil},
			{txID: 1, opType: "rollback", expected: nil},
		},
		expected: []expectedResult{
			{storeID: 0, key: "key1", value: ""},
		},
	},
	{
		description: "read after write in same transaction",
		operations: []operation{
			{txID: 1, opType: "begin", expected: nil},
			{txID: 1, opType: "set", storeID: 0, key: "key1", value: "value1", expected: nil},
			{txID: 1, opType: "get", storeID: 0, key: "key1", value: "value1", expected: nil},
			{txID: 1, opType: "commit", expected: nil},
		},
		expected: []expectedResult{
			{storeID: 0, key: "key1", value: "value1"},
		},
	},
}