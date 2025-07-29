package raft_log

var consistencyCheckTestCases = []struct {
	name     string
	leader   []LogEntry
	follower []LogEntry
	want     int
}{
	{
		name:     "empty logs",
		leader:   []LogEntry{},
		follower: []LogEntry{},
		want:     -1,
	},
	{
		name:     "follower behind",
		leader:   []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}},
		follower: []LogEntry{{Term: 1, Data: "a"}},
		want:     0,
	},
	{
		name:     "follower ahead but matching",
		leader:   []LogEntry{{Term: 1, Data: "a"}},
		follower: []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}},
		want:     0,
	},
	{
		name:     "completely divergent",
		leader:   []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}},
		follower: []LogEntry{{Term: 1, Data: "x"}, {Term: 1, Data: "y"}},
		want:     -1,
	},
	{
		name:     "partial match",
		leader:   []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}, {Term: 2, Data: "c"}},
		follower: []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "x"}, {Term: 1, Data: "y"}},
		want:     0,
	},
}

var truncateTestCases = []struct {
	name    string
	entries []LogEntry
	index   int
	wantLen int
}{
	{
		name:    "truncate middle",
		entries: []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}, {Term: 1, Data: "c"}},
		index:   1,
		wantLen: 1,
	},
	{
		name:    "truncate all",
		entries: []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}},
		index:   0,
		wantLen: 0,
	},
	{
		name:    "truncate none",
		entries: []LogEntry{{Term: 1, Data: "a"}},
		index:   1,
		wantLen: 1,
	},
}