package transaction_ordering

import "time"

type testCase struct {
	name          string
	transactions  []Transaction
	initialBalances map[int]int
	expectedRejected []Transaction
	expectedBalances map[int]int
}

var testCases = []testCase{
	{
		name: "simple transfer",
		transactions: []Transaction{
			{From: 1, To: 2, Amount: 100, Timestamp: time.Unix(1678886400, 0)},
		},
		initialBalances: map[int]int{1: 200, 2: 0},
		expectedRejected: []Transaction{},
		expectedBalances: map[int]int{1: 100, 2: 100},
	},
	{
		name: "multiple transfers",
		transactions: []Transaction{
			{From: 1, To: 2, Amount: 100, Timestamp: time.Unix(1678886400, 0)},
			{From: 2, To: 3, Amount: 50, Timestamp: time.Unix(1678886401, 0)},
		},
		initialBalances: map[int]int{1: 200, 2: 0, 3: 0},
		expectedRejected: []Transaction{},
		expectedBalances: map[int]int{1: 100, 2: 50, 3: 50},
	},
	{
		name: "insufficient funds",
		transactions: []Transaction{
			{From: 1, To: 2, Amount: 200, Timestamp: time.Unix(1678886400, 0)},
			{From: 1, To: 3, Amount: 50, Timestamp: time.Unix(1678886401, 0)},
		},
		initialBalances: map[int]int{1: 100, 2: 0, 3: 0},
		expectedRejected: []Transaction{
			{From: 1, To: 2, Amount: 200, Timestamp: time.Unix(1678886400, 0)},
		},
		expectedBalances: map[int]int{1: 50, 2: 0, 3: 50},
	},
	{
		name: "timestamp ordering",
		transactions: []Transaction{
			{From: 1, To: 2, Amount: 100, Timestamp: time.Unix(1678886401, 0)},
			{From: 1, To: 3, Amount: 50, Timestamp: time.Unix(1678886400, 0)},
		},
		initialBalances: map[int]int{1: 200, 2: 0, 3: 0},
		expectedRejected: []Transaction{},
		expectedBalances: map[int]int{1: 50, 2: 100, 3: 50},
	},
	{
		name: "tie breaker by account id",
		transactions: []Transaction{
			{From: 2, To: 3, Amount: 50, Timestamp: time.Unix(1678886400, 0)},
			{From: 1, To: 3, Amount: 100, Timestamp: time.Unix(1678886400, 0)},
		},
		initialBalances: map[int]int{1: 200, 2: 200, 3: 0},
		expectedRejected: []Transaction{},
		expectedBalances: map[int]int{1: 100, 2: 150, 3: 150},
	},
}