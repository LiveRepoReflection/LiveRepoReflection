package dist_cache

type testCase struct {
	description string
	operations  []operation
	expected    []result
}

type operation struct {
	op    string
	key   string
	value string
}

type result struct {
	value  string
	exists bool
	err    bool
}

var testCases = []testCase{
	{
		description: "basic operations",
		operations: []operation{
			{"put", "key1", "value1"},
			{"get", "key1", ""},
			{"put", "key2", "value2"},
			{"get", "key2", ""},
			{"get", "key3", ""},
		},
		expected: []result{
			{"", false, false},
			{"value1", true, false},
			{"", false, false},
			{"value2", true, false},
			{"", false, false},
		},
	},
	{
		description: "overwrite existing key",
		operations: []operation{
			{"put", "key1", "value1"},
			{"put", "key1", "value2"},
			{"get", "key1", ""},
		},
		expected: []result{
			{"", false, false},
			{"", false, false},
			{"value2", true, false},
		},
	},
	{
		description: "large dataset",
		operations: []operation{
			{"put", "key1", string(make([]byte, 1024*1024))}, // 1MB value
			{"get", "key1", ""},
		},
		expected: []result{
			{"", false, false},
			{string(make([]byte, 1024*1024)), true, false},
		},
	},
}