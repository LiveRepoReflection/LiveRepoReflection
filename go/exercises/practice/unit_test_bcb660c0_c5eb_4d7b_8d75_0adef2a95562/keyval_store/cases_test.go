package keyval_store

var testCases = []struct {
	name        string
	key         string
	value       string
	startKey    string
	endKey      string
	expectedVal string
	expectedLen int
	expectedCnt int
}{
	{
		name:        "basic put and get",
		key:         "test1",
		value:       "value1",
		expectedVal: "value1",
	},
	{
		name:        "empty value",
		key:         "empty_val",
		value:       "",
		expectedVal: "",
	},
	{
		name:        "range query single item",
		key:         "range1",
		value:       "rvalue1",
		startKey:    "range1",
		endKey:      "range2",
		expectedLen: 1,
	},
	{
		name:        "range query multiple items",
		key:         "range2",
		value:       "rvalue2",
		startKey:    "range1",
		endKey:      "range3",
		expectedLen: 2,
	},
	{
		name:        "count query",
		key:         "count1",
		value:       "cvalue1",
		startKey:    "count1",
		endKey:      "count2",
		expectedCnt: 1,
	},
}