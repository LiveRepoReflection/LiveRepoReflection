package graph_evolution

type testCase struct {
	description    string
	n              int
	initialGraph   [][]bool
	evolutionRules []EvolutionRule
	timeSteps      int
	expectedGraph  [][]bool
}

var testCases = []testCase{
	{
		description: "no evolution rules",
		n:           3,
		initialGraph: [][]bool{
			{false, true, false},
			{false, false, true},
			{true, false, false},
		},
		evolutionRules: []EvolutionRule{},
		timeSteps:      100,
		expectedGraph: [][]bool{
			{false, true, false},
			{false, false, true},
			{true, false, false},
		},
	},
	{
		description: "certain follow rule",
		n:           2,
		initialGraph: [][]bool{
			{false, false},
			{false, false},
		},
		evolutionRules: []EvolutionRule{
			{SourceUser: 0, TargetUser: 1, ActionType: "follow", Probability: 1.0},
		},
		timeSteps: 1,
		expectedGraph: [][]bool{
			{false, true},
			{false, false},
		},
	},
	{
		description: "certain unfollow rule",
		n:           2,
		initialGraph: [][]bool{
			{false, true},
			{false, false},
		},
		evolutionRules: []EvolutionRule{
			{SourceUser: 0, TargetUser: 1, ActionType: "unfollow", Probability: 1.0},
		},
		timeSteps: 1,
		expectedGraph: [][]bool{
			{false, false},
			{false, false},
		},
	},
	{
		description: "multiple rules with different probabilities",
		n:           3,
		initialGraph: [][]bool{
			{false, false, false},
			{false, false, false},
			{false, false, false},
		},
		evolutionRules: []EvolutionRule{
			{SourceUser: 0, TargetUser: 1, ActionType: "follow", Probability: 0.3},
			{SourceUser: 1, TargetUser: 2, ActionType: "follow", Probability: 0.7},
			{SourceUser: 2, TargetUser: 0, ActionType: "follow", Probability: 0.5},
		},
		timeSteps:     10,
		expectedGraph: nil, // Will be checked in probabilistic test
	},
}