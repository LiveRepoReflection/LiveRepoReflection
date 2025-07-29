package efficient_router

// This file contains test cases for the efficient_router package

// Test cases for routing rule matching
var routingRuleTests = []struct {
	description    string
	routingRules   []Rule
	ipAddresses    []string
	expectedNextHops []string
}{
	{
		description: "basic test case with single rule",
		routingRules: []Rule{
			{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
		},
		ipAddresses: []string{
			"192.168.1.1",
			"10.0.0.1",
		},
		expectedNextHops: []string{
			"RouterA",
			"DROP",
		},
	},
	{
		description: "multiple rules with different prefix lengths",
		routingRules: []Rule{
			{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
			{Prefix: "192.168.0.0/16", NextHop: "RouterB", Metric: 20},
			{Prefix: "0.0.0.0/0", NextHop: "RouterC", Metric: 30},
		},
		ipAddresses: []string{
			"192.168.1.1",
			"192.168.2.1",
			"10.0.0.1",
		},
		expectedNextHops: []string{
			"RouterA",
			"RouterB",
			"RouterC",
		},
	},
	{
		description: "rules with same prefix but different metrics",
		routingRules: []Rule{
			{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
			{Prefix: "192.168.1.0/24", NextHop: "RouterB", Metric: 5},
			{Prefix: "0.0.0.0/0", NextHop: "RouterC", Metric: 30},
		},
		ipAddresses: []string{
			"192.168.1.1",
			"10.0.0.1",
		},
		expectedNextHops: []string{
			"RouterB",
			"RouterC",
		},
	},
	{
		description: "example from the problem statement",
		routingRules: []Rule{
			{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
			{Prefix: "192.168.0.0/16", NextHop: "RouterB", Metric: 20},
			{Prefix: "0.0.0.0/0", NextHop: "RouterC", Metric: 30},
			{Prefix: "192.168.1.5/32", NextHop: "RouterD", Metric: 5},
		},
		ipAddresses: []string{
			"192.168.1.1",
			"10.0.0.1",
			"192.168.1.5",
		},
		expectedNextHops: []string{
			"RouterA",
			"RouterC",
			"RouterD",
		},
	},
	{
		description: "complex overlapping prefixes",
		routingRules: []Rule{
			{Prefix: "172.16.0.0/12", NextHop: "RouterA", Metric: 10},
			{Prefix: "172.16.0.0/16", NextHop: "RouterB", Metric: 20},
			{Prefix: "172.16.1.0/24", NextHop: "RouterC", Metric: 30},
			{Prefix: "172.16.1.0/24", NextHop: "RouterD", Metric: 5},
			{Prefix: "172.16.1.128/25", NextHop: "RouterE", Metric: 15},
		},
		ipAddresses: []string{
			"172.16.0.1",    // Should match 172.16.0.0/16
			"172.16.1.1",    // Should match 172.16.1.0/24 with lowest metric (RouterD)
			"172.16.1.200",  // Should match 172.16.1.128/25
			"172.17.1.1",    // Should match 172.16.0.0/12
		},
		expectedNextHops: []string{
			"RouterB",
			"RouterD",
			"RouterE",
			"RouterA",
		},
	},
	{
		description: "limit case - no match",
		routingRules: []Rule{
			{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
		},
		ipAddresses: []string{
			"10.0.0.1",
		},
		expectedNextHops: []string{
			"DROP",
		},
	},
	{
		description: "limit case - exact IP match with /32",
		routingRules: []Rule{
			{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
			{Prefix: "192.168.1.42/32", NextHop: "RouterB", Metric: 5},
		},
		ipAddresses: []string{
			"192.168.1.42",
		},
		expectedNextHops: []string{
			"RouterB",
		},
	},
}

// Test cases for large routing tables
var largeRoutingTableTests = []struct {
	description    string
	routingRuleCount int
	ipAddressCount   int
}{
	{
		description: "medium routing table",
		routingRuleCount: 1000,
		ipAddressCount: 100,
	},
	{
		description: "large routing table",
		routingRuleCount: 10000,
		ipAddressCount: 1000,
	},
}