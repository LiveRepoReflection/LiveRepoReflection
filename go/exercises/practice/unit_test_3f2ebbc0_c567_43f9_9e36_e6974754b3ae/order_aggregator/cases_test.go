package order_aggregator

type orderBookTest struct {
	description string
	input       [][]struct {
		Price    float64
		Quantity int
		NodeID   int
	}
	k              int
	expectedBuy    []struct {
		Price    float64
		Quantity int
		NodeID   int
	}
	expectedSell   []struct {
		Price    float64
		Quantity int
		NodeID   int
	}
}

var testCases = []orderBookTest{
	{
		description: "empty order books",
		input:       [][]struct{Price float64; Quantity int; NodeID int}{},
		k:           2,
		expectedBuy: []struct{Price float64; Quantity int; NodeID int}{},
		expectedSell: []struct{Price float64; Quantity int; NodeID int}{},
	},
	{
		description: "single node with one order",
		input: [][]struct{Price float64; Quantity int; NodeID int}{
			{{10.0, 5, 1}},
		},
		k: 1,
		expectedBuy: []struct{Price float64; Quantity int; NodeID int}{
			{10.0, 5, 1},
		},
		expectedSell: []struct{Price float64; Quantity int; NodeID int}{
			{10.0, 5, 1},
		},
	},
	{
		description: "multiple nodes with overlapping prices",
		input: [][]struct{Price float64; Quantity int; NodeID int}{
			{{10.0, 5, 1}, {9.5, 3, 1}},
			{{10.5, 2, 2}, {9.8, 4, 2}},
		},
		k: 2,
		expectedBuy: []struct{Price float64; Quantity int; NodeID int}{
			{10.5, 2, 2},
			{10.0, 5, 1},
		},
		expectedSell: []struct{Price float64; Quantity int; NodeID int}{
			{9.5, 3, 1},
			{9.8, 4, 2},
		},
	},
	{
		description: "tie-breaker by node ID",
		input: [][]struct{Price float64; Quantity int; NodeID int}{
			{{10.0, 5, 2}},
			{{10.0, 3, 1}},
		},
		k: 1,
		expectedBuy: []struct{Price float64; Quantity int; NodeID int}{
			{10.0, 3, 1},
		},
		expectedSell: []struct{Price float64; Quantity int; NodeID int}{
			{10.0, 3, 1},
		},
	},
	{
		description: "K larger than available orders",
		input: [][]struct{Price float64; Quantity int; NodeID int}{
			{{10.0, 5, 1}, {9.5, 3, 1}},
		},
		k: 5,
		expectedBuy: []struct{Price float64; Quantity int; NodeID int}{
			{10.0, 5, 1},
			{9.5, 3, 1},
		},
		expectedSell: []struct{Price float64; Quantity int; NodeID int}{
			{9.5, 3, 1},
			{10.0, 5, 1},
		},
	},
}