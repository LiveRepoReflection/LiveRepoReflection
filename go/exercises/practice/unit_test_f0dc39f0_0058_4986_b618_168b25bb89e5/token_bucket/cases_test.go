package tokenbucket

type tenantConfig struct {
	capacity   int
	refillRate float64
}

type allowTestCase struct {
	description   string
	tenantID     string
	tokens       int
	shouldAllow  bool
	initialLimit tenantConfig
}

type concurrentTestCase struct {
	description string
	operations  []struct {
		tenantID string
		tokens   int
	}
	expected []bool
}

var singleTenantTestCases = []allowTestCase{
	{
		description:   "basic allow within capacity",
		tenantID:     "tenant1",
		tokens:       5,
		shouldAllow:  true,
		initialLimit: tenantConfig{capacity: 10, refillRate: 1.0},
	},
	{
		description:   "exceed capacity",
		tenantID:     "tenant1",
		tokens:       15,
		shouldAllow:  false,
		initialLimit: tenantConfig{capacity: 10, refillRate: 1.0},
	},
	{
		description:   "zero capacity",
		tenantID:     "tenant1",
		tokens:       1,
		shouldAllow:  false,
		initialLimit: tenantConfig{capacity: 0, refillRate: 1.0},
	},
	{
		description:   "negative tokens request",
		tenantID:     "tenant1",
		tokens:       -1,
		shouldAllow:  false,
		initialLimit: tenantConfig{capacity: 10, refillRate: 1.0},
	},
}

var multiTenantTestCases = []struct {
	description string
	tenants     map[string]tenantConfig
	operations  []struct {
		tenantID string
		tokens   int
	}
	expected []bool
}{
	{
		description: "multiple tenants with different configs",
		tenants: map[string]tenantConfig{
			"tenant1": {capacity: 10, refillRate: 1.0},
			"tenant2": {capacity: 5, refillRate: 0.5},
		},
		operations: []struct {
			tenantID string
			tokens   int
		}{
			{"tenant1", 5},
			{"tenant2", 3},
			{"tenant1", 6},
			{"tenant2", 3},
		},
		expected: []bool{true, true, false, false},
	},
}

var refillTestCases = []struct {
	description     string
	initialConfig   tenantConfig
	waitSeconds     float64
	expectedTokens  float64
	requestedTokens int
	shouldAllow     bool
}{
	{
		description:     "partial refill",
		initialConfig:   tenantConfig{capacity: 10, refillRate: 1.0},
		waitSeconds:     0.5,
		expectedTokens:  0.5,
		requestedTokens: 1,
		shouldAllow:     false,
	},
	{
		description:     "full refill",
		initialConfig:   tenantConfig{capacity: 10, refillRate: 2.0},
		waitSeconds:     5.0,
		expectedTokens:  10.0,
		requestedTokens: 10,
		shouldAllow:     true,
	},
}