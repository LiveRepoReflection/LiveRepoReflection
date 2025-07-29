package dtc_banking

// This is the test cases file for the distributed transaction coordinator banking system.

type account struct {
	ID      string
	Balance int
}

type bankService struct {
	ID       string
	Accounts map[string]*account
}

type testCase struct {
	description       string
	initialBanks      []bankService
	transactions      []Transaction
	expectedAccounts  map[string]map[string]int // bankID -> accountID -> balance
	expectErrors      bool
	simulateFailures  bool
	concurrentExecute bool
}

var testCases = []testCase{
	{
		description: "Simple successful transaction",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
					"acc2": {ID: "acc2", Balance: 50},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank1", DestAccountID: "acc2", Amount: 30},
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 70,
				"acc2": 80,
			},
		},
		expectErrors:      false,
		simulateFailures:  false,
		concurrentExecute: false,
	},
	{
		description: "Cross-bank transaction",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
				},
			},
			{
				ID: "bank2",
				Accounts: map[string]*account{
					"acc2": {ID: "acc2", Balance: 50},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank2", DestAccountID: "acc2", Amount: 30},
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 70,
			},
			"bank2": {
				"acc2": 80,
			},
		},
		expectErrors:      false,
		simulateFailures:  false,
		concurrentExecute: false,
	},
	{
		description: "Transaction with insufficient funds should fail",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
					"acc2": {ID: "acc2", Balance: 50},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank1", DestAccountID: "acc2", Amount: 150},
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 100,
				"acc2": 50,
			},
		},
		expectErrors:      true,
		simulateFailures:  false,
		concurrentExecute: false,
	},
	{
		description: "Complex transaction with multiple operations",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
					"acc2": {ID: "acc2", Balance: 50},
				},
			},
			{
				ID: "bank2",
				Accounts: map[string]*account{
					"acc3": {ID: "acc3", Balance: 200},
					"acc4": {ID: "acc4", Balance: 75},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank2", DestAccountID: "acc3", Amount: 30},
					{SourceBankID: "bank2", SourceAccountID: "acc4", DestBankID: "bank1", DestAccountID: "acc2", Amount: 25},
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 70,
				"acc2": 75,
			},
			"bank2": {
				"acc3": 230,
				"acc4": 50,
			},
		},
		expectErrors:      false,
		simulateFailures:  false,
		concurrentExecute: false,
	},
	{
		description: "Concurrent transactions",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
					"acc2": {ID: "acc2", Balance: 100},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank1", DestAccountID: "acc2", Amount: 30},
				},
			},
			{
				ID: "tx2",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc2", DestBankID: "bank1", DestAccountID: "acc1", Amount: 20},
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 90,
				"acc2": 110,
			},
		},
		expectErrors:      false,
		simulateFailures:  false,
		concurrentExecute: true,
	},
	{
		description: "Transaction with simulated failures should eventually succeed",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
				},
			},
			{
				ID: "bank2",
				Accounts: map[string]*account{
					"acc2": {ID: "acc2", Balance: 50},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank2", DestAccountID: "acc2", Amount: 30},
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 70,
			},
			"bank2": {
				"acc2": 80,
			},
		},
		expectErrors:      false,
		simulateFailures:  true,
		concurrentExecute: false,
	},
	{
		description: "Multiple transactions with mixed success/failure outcomes",
		initialBanks: []bankService{
			{
				ID: "bank1",
				Accounts: map[string]*account{
					"acc1": {ID: "acc1", Balance: 100},
					"acc2": {ID: "acc2", Balance: 50},
				},
			},
			{
				ID: "bank2",
				Accounts: map[string]*account{
					"acc3": {ID: "acc3", Balance: 200},
				},
			},
		},
		transactions: []Transaction{
			{
				ID: "tx1",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc1", DestBankID: "bank2", DestAccountID: "acc3", Amount: 30},
				},
			},
			{
				ID: "tx2",
				Operations: []Operation{
					{SourceBankID: "bank1", SourceAccountID: "acc2", DestBankID: "bank2", DestAccountID: "acc3", Amount: 60}, // Will fail due to insufficient funds
				},
			},
		},
		expectedAccounts: map[string]map[string]int{
			"bank1": {
				"acc1": 70,
				"acc2": 50, // Unchanged because tx2 fails
			},
			"bank2": {
				"acc3": 230, // Only tx1 succeeds
			},
		},
		expectErrors:      true,
		simulateFailures:  false,
		concurrentExecute: false,
	},
}