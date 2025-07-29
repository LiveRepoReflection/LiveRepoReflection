package traffic_sim

var testCases = []struct {
	description        string
	network           map[string]map[string]int
	initialDistribution map[string]int
	steps             int
	expected          map[string]int
}{
	{
		description: "single road",
		network: map[string]map[string]int{
			"A": {"B": 5},
			"B": {"A": 5},
		},
		initialDistribution: map[string]int{
			"A": 3,
			"B": 2,
		},
		steps: 1,
		expected: map[string]int{
			"A": 2,
			"B": 3,
		},
	},
	{
		description: "circular network",
		network: map[string]map[string]int{
			"A": {"B": 2},
			"B": {"C": 2},
			"C": {"A": 2},
		},
		initialDistribution: map[string]int{
			"A": 3,
			"B": 0,
			"C": 0,
		},
		steps: 3,
		expected: map[string]int{
			"A": 1,
			"B": 1,
			"C": 1,
		},
	},
}