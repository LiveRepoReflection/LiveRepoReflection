package ratelimiter

type testCase struct {
	description string
	setup      func(rl RateLimiter)
	action     func(rl RateLimiter) (bool, error)
	expected   bool
	expectErr  bool
}

var testCases = []testCase{
	{
		description: "Basic allow",
		setup: func(rl RateLimiter) {
			rl.SetClientLimit("c1", 10)
			rl.SetResourceWeight("r1", 1)
		},
		action: func(rl RateLimiter) (bool, error) {
			return rl.Allow("c1", "r1")
		},
		expected:  true,
		expectErr: false,
	},
	{
		description: "Exceed limit",
		setup: func(rl RateLimiter) {
			rl.SetClientLimit("c2", 5)
			rl.SetResourceWeight("r2", 3)
		},
		action: func(rl RateLimiter) (bool, error) {
			rl.Allow("c2", "r2")
			return rl.Allow("c2", "r2")
		},
		expected:  false,
		expectErr: false,
	},
	{
		description: "Nonexistent client",
		setup:      func(rl RateLimiter) {},
		action: func(rl RateLimiter) (bool, error) {
			return rl.Allow("nonexistent", "r1")
		},
		expected:  false,
		expectErr: true,
	},
	{
		description: "Nonexistent resource",
		setup: func(rl RateLimiter) {
			rl.SetClientLimit("c3", 10)
		},
		action: func(rl RateLimiter) (bool, error) {
			return rl.Allow("c3", "nonexistent")
		},
		expected:  false,
		expectErr: true,
	},
}