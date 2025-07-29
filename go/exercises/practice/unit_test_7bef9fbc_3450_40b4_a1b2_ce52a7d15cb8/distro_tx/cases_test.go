package distrotx

// Test cases for the distributed transaction coordinator
var testCases = []struct {
	description   string
	participants  []Participant
	prepareDelay  map[string]int // Simulated delay in ms for prepare phase
	commitDelay   map[string]int // Simulated delay in ms for commit phase
	rollbackDelay map[string]int // Simulated delay in ms for rollback phase
	prepareError  map[string]bool // Should participant return error on prepare
	commitError   map[string]bool // Should participant return error on commit
	shouldCommit  bool           // Expected outcome: commit or rollback
	expectedErr   bool           // Should coordinator return an error
}{
	{
		description: "successful transaction with two participants",
		participants: []Participant{
			{ServiceURL: "http://service-a:8080", Timeout: 1000},
			{ServiceURL: "http://service-b:8080", Timeout: 1000},
		},
		prepareDelay:  map[string]int{},
		commitDelay:   map[string]int{},
		rollbackDelay: map[string]int{},
		prepareError:  map[string]bool{},
		commitError:   map[string]bool{},
		shouldCommit:  true,
		expectedErr:   false,
	},
	{
		description: "one participant fails prepare phase",
		participants: []Participant{
			{ServiceURL: "http://service-a:8080", Timeout: 1000},
			{ServiceURL: "http://service-b:8080", Timeout: 1000},
		},
		prepareDelay:  map[string]int{},
		commitDelay:   map[string]int{},
		rollbackDelay: map[string]int{},
		prepareError: map[string]bool{
			"http://service-b:8080": true,
		},
		commitError:  map[string]bool{},
		shouldCommit: false,
		expectedErr:  true,
	},
	{
		description: "participant timeout during prepare",
		participants: []Participant{
			{ServiceURL: "http://service-a:8080", Timeout: 100},
			{ServiceURL: "http://service-b:8080", Timeout: 100},
		},
		prepareDelay: map[string]int{
			"http://service-b:8080": 200,
		},
		commitDelay:   map[string]int{},
		rollbackDelay: map[string]int{},
		prepareError:  map[string]bool{},
		commitError:   map[string]bool{},
		shouldCommit:  false,
		expectedErr:   true,
	},
	{
		description: "max participants exceeded",
		participants: make([]Participant, 11), // Exceeds max of 10
		prepareDelay:  map[string]int{},
		commitDelay:   map[string]int{},
		rollbackDelay: map[string]int{},
		prepareError:  map[string]bool{},
		commitError:   map[string]bool{},
		shouldCommit:  false,
		expectedErr:   true,
	},
}