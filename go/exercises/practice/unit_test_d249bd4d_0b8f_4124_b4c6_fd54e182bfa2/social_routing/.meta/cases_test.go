package socialrouting

// Test cases for the social network routing problem
var testCases = []struct {
	description string
	network     map[string][]string
	startUser   string
	endUser     string
	maxHops     int
	blacklist   []string
	expected    []string
}{
	{
		description: "direct connection - 1 hop",
		network: map[string][]string{
			"alice":   {"bob", "charlie"},
			"bob":     {"alice", "david"},
			"charlie": {"alice"},
			"david":   {"bob"},
		},
		startUser: "alice",
		endUser:   "bob",
		maxHops:   5,
		blacklist: []string{},
		expected:  []string{"alice", "bob"},
	},
	{
		description: "two hops needed",
		network: map[string][]string{
			"alice":   {"bob", "charlie"},
			"bob":     {"alice", "david"},
			"charlie": {"alice", "eve"},
			"david":   {"bob"},
			"eve":     {"charlie", "frank"},
			"frank":   {"eve"},
		},
		startUser: "alice",
		endUser:   "frank",
		maxHops:   5,
		blacklist: []string{},
		expected:  []string{"alice", "charlie", "eve", "frank"},
	},
	{
		description: "multiple possible paths, should find shortest",
		network: map[string][]string{
			"alice":   {"bob", "charlie", "dave"},
			"bob":     {"alice", "eve"},
			"charlie": {"alice", "eve"},
			"dave":    {"alice", "eve"},
			"eve":     {"bob", "charlie", "dave", "frank"},
			"frank":   {"eve"},
		},
		startUser: "alice",
		endUser:   "frank",
		maxHops:   5,
		blacklist: []string{},
		expected:  []string{"alice", "bob", "eve", "frank"}, // Any of the three 3-hop paths is valid
	},
	{
		description: "blacklisted nodes - must find alternative route",
		network: map[string][]string{
			"alice":   {"bob", "charlie"},
			"bob":     {"alice", "david", "eve"},
			"charlie": {"alice", "frank"},
			"david":   {"bob", "eve"},
			"eve":     {"bob", "david", "frank"},
			"frank":   {"charlie", "eve"},
		},
		startUser: "alice",
		endUser:   "frank",
		maxHops:   5,
		blacklist: []string{"eve"},
		expected:  []string{"alice", "charlie", "frank"},
	},
	{
		description: "no path exists with max hops constraint",
		network: map[string][]string{
			"alice":   {"bob"},
			"bob":     {"alice", "charlie"},
			"charlie": {"bob", "david"},
			"david":   {"charlie", "eve"},
			"eve":     {"david", "frank"},
			"frank":   {"eve"},
		},
		startUser: "alice",
		endUser:   "frank",
		maxHops:   3, // Need 5 hops but max is 3
		blacklist: []string{},
		expected:  []string{}, // No path within max hops
	},
	{
		description: "same start and end user",
		network: map[string][]string{
			"alice": {"bob"},
			"bob":   {"alice"},
		},
		startUser: "alice",
		endUser:   "alice",
		maxHops:   5,
		blacklist: []string{},
		expected:  []string{"alice"}, // Start and end are the same
	},
	{
		description: "start user not in network",
		network: map[string][]string{
			"bob":   {"charlie"},
			"charlie": {"bob"},
		},
		startUser: "alice", // Not in network
		endUser:   "bob",
		maxHops:   5,
		blacklist: []string{},
		expected:  []string{}, // Start user not found
	},
	{
		description: "end user not in network",
		network: map[string][]string{
			"alice": {"bob"},
			"bob":   {"alice"},
		},
		startUser: "alice",
		endUser:   "charlie", // Not in network
		maxHops:   5,
		blacklist: []string{},
		expected:  []string{}, // End user not found
	},
	{
		description: "all paths blocked by blacklist",
		network: map[string][]string{
			"alice":   {"bob", "charlie"},
			"bob":     {"alice", "david"},
			"charlie": {"alice", "david"},
			"david":   {"bob", "charlie", "eve"},
			"eve":     {"david"},
		},
		startUser: "alice",
		endUser:   "eve",
		maxHops:   5,
		blacklist: []string{"bob", "charlie", "david"}, // All intermediaries blocked
		expected:  []string{}, // No path possible due to blacklist
	},
	{
		description: "complex network with multiple paths",
		network: map[string][]string{
			"a": {"b", "c", "d"},
			"b": {"a", "e", "f"},
			"c": {"a", "g", "h"},
			"d": {"a", "i", "j"},
			"e": {"b", "k"},
			"f": {"b", "l"},
			"g": {"c", "m"},
			"h": {"c", "n"},
			"i": {"d", "o"},
			"j": {"d", "p"},
			"k": {"e", "q"},
			"l": {"f", "q"},
			"m": {"g", "r"},
			"n": {"h", "r"},
			"o": {"i", "s"},
			"p": {"j", "s"},
			"q": {"k", "l", "t"},
			"r": {"m", "n", "t"},
			"s": {"o", "p", "t"},
			"t": {"q", "r", "s"},
		},
		startUser: "a",
		endUser:   "t",
		maxHops:   5,
		blacklist: []string{"e", "g", "i", "m", "o", "p"},
		expected:  []string{"a", "b", "f", "l", "q", "t"}, // One of the valid shortest paths
	},
}