package leakybucket

type leakyBucketTest struct {
	description string
	userID      string
	capacity    int
	leakRate    float64
	requests    []struct {
		timestamp int64  // Unix timestamp in milliseconds
		expected  bool   // Whether the request should be allowed
		comment   string // Description of the test case
	}
}

var testCases = []leakyBucketTest{
	{
		description: "single user basic test",
		userID:      "user1",
		capacity:    3,
		leakRate:    1.0, // 1 request per second
		requests: []struct {
			timestamp int64
			expected  bool
			comment   string
		}{
			{1000, true, "first request should be allowed"},
			{1100, true, "second request should be allowed"},
			{1200, true, "third request should be allowed"},
			{1300, false, "fourth request should be blocked (bucket full)"},
			{2500, true, "request should be allowed after leak"},
		},
	},
	{
		description: "multiple users test",
		userID:      "user2",
		capacity:    2,
		leakRate:    0.5, // 1 request per 2 seconds
		requests: []struct {
			timestamp int64
			expected  bool
			comment   string
		}{
			{1000, true, "first request should be allowed"},
			{1100, true, "second request should be allowed"},
			{1200, false, "third request should be blocked"},
			{3500, true, "request should be allowed after leak"},
		},
	},
	{
		description: "high rate test",
		userID:      "user3",
		capacity:    1000,
		leakRate:    100.0, // 100 requests per second
		requests: []struct {
			timestamp int64
			expected  bool
			comment   string
		}{
			{1000, true, "first request should be allowed"},
			{1001, true, "second request should be allowed"},
			{1002, true, "third request should be allowed"},
			{1003, true, "fourth request should be allowed"},
			{1004, true, "fifth request should be allowed"},
		},
	},
	{
		description: "zero capacity test",
		userID:      "user4",
		capacity:    0,
		leakRate:    1.0,
		requests: []struct {
			timestamp int64
			expected  bool
			comment   string
		}{
			{1000, false, "request should be blocked with zero capacity"},
			{2000, false, "request should be blocked with zero capacity"},
		},
	},
	{
		description: "zero leak rate test",
		userID:      "user5",
		capacity:    1,
		leakRate:    0.0,
		requests: []struct {
			timestamp int64
			expected  bool
			comment   string
		}{
			{1000, true, "first request should be allowed"},
			{2000, false, "subsequent requests should be blocked with zero leak rate"},
			{3000, false, "subsequent requests should be blocked with zero leak rate"},
		},
	},
}