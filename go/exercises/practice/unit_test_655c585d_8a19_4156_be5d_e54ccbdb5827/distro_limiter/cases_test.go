package distrolimiter

type testCase struct {
	description    string
	key           string
	ratePerSecond int
	burstCapacity int
	operations    []operation
	expected      []bool
}

type operation struct {
	delay    int // delay in milliseconds before operation
	expected bool
}

var testCases = []testCase{
	{
		description:    "Basic rate limiting",
		key:           "user1",
		ratePerSecond: 2,
		burstCapacity: 2,
		operations: []operation{
			{delay: 0, expected: true},
			{delay: 0, expected: true},
			{delay: 0, expected: false},
			{delay: 1000, expected: true},
		},
	},
	{
		description:    "Burst capacity test",
		key:           "user2",
		ratePerSecond: 1,
		burstCapacity: 3,
		operations: []operation{
			{delay: 0, expected: true},
			{delay: 0, expected: true},
			{delay: 0, expected: true},
			{delay: 0, expected: false},
			{delay: 1000, expected: true},
		},
	},
	{
		description:    "Rate refresh test",
		key:           "user3",
		ratePerSecond: 1,
		burstCapacity: 1,
		operations: []operation{
			{delay: 0, expected: true},
			{delay: 0, expected: false},
			{delay: 1000, expected: true},
			{delay: 500, expected: false},
			{delay: 500, expected: true},
		},
	},
}