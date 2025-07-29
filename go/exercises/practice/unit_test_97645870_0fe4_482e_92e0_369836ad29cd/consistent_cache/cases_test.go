package consistentcache

// Test cases for the distributed consistent cache implementation
var testCases = []struct {
	description string
	operations  []CacheOperation
	expected    []CacheResult
}{
	{
		description: "basic single node operations",
		operations: []CacheOperation{
			{op: "Set", key: "key1", value: "value1"},
			{op: "Get", key: "key1"},
			{op: "Delete", key: "key1"},
			{op: "Get", key: "key1"},
		},
		expected: []CacheResult{
			{value: "", exists: true},
			{value: "value1", exists: true},
			{value: "", exists: true},
			{value: "", exists: false},
		},
	},
	{
		description: "concurrent operations on multiple nodes",
		operations: []CacheOperation{
			{op: "Set", key: "key1", value: "value1"},
			{op: "Set", key: "key2", value: "value2"},
			{op: "Set", key: "key3", value: "value3"},
			{op: "Get", key: "key1"},
			{op: "Get", key: "key2"},
			{op: "Get", key: "key3"},
		},
		expected: []CacheResult{
			{value: "", exists: true},
			{value: "", exists: true},
			{value: "", exists: true},
			{value: "value1", exists: true},
			{value: "value2", exists: true},
			{value: "value3", exists: true},
		},
	},
	{
		description: "overwrite existing keys",
		operations: []CacheOperation{
			{op: "Set", key: "key1", value: "value1"},
			{op: "Set", key: "key1", value: "newvalue1"},
			{op: "Get", key: "key1"},
		},
		expected: []CacheResult{
			{value: "", exists: true},
			{value: "", exists: true},
			{value: "newvalue1", exists: true},
		},
	},
	{
		description: "delete non-existent key",
		operations: []CacheOperation{
			{op: "Delete", key: "nonexistent"},
			{op: "Get", key: "nonexistent"},
		},
		expected: []CacheResult{
			{value: "", exists: true},
			{value: "", exists: false},
		},
	},
}
