package raft_log

import (
	"math/rand"
	"sync"
	"testing"
	"time"
)

func TestLogAppendAndGet(t *testing.T) {
	log := NewLog()
	entries := []LogEntry{
		{Term: 1, Data: "cmd1"},
		{Term: 1, Data: "cmd2"},
		{Term: 2, Data: "cmd3"},
	}

	for _, entry := range entries {
		log.Append(entry)
	}

	for i, expected := range entries {
		actual, err := log.Get(i)
		if err != nil {
			t.Errorf("Get(%d) returned error: %v", i, err)
		}
		if actual != expected {
			t.Errorf("Get(%d) = %v, want %v", i, actual, expected)
		}
	}
}

func TestLogConsistencyCheck(t *testing.T) {
	tests := []struct {
		name     string
		leader   []LogEntry
		follower []LogEntry
		want     int
	}{
		{
			name:     "identical logs",
			leader:   []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}},
			follower: []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "b"}},
			want:     1,
		},
		{
			name:     "divergent logs",
			leader:   []LogEntry{{Term: 1, Data: "a"}, {Term: 2, Data: "b"}},
			follower: []LogEntry{{Term: 1, Data: "a"}, {Term: 1, Data: "x"}},
			want:     0,
		},
		{
			name:     "empty follower",
			leader:   []LogEntry{{Term: 1, Data: "a"}},
			follower: []LogEntry{},
			want:     -1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			leaderLog := NewLog()
			followerLog := NewLog()
			for _, entry := range tt.leader {
				leaderLog.Append(entry)
			}
			for _, entry := range tt.follower {
				followerLog.Append(entry)
			}

			got := ConsistencyCheck(leaderLog, followerLog)
			if got != tt.want {
				t.Errorf("ConsistencyCheck() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestLogTruncate(t *testing.T) {
	log := NewLog()
	entries := []LogEntry{
		{Term: 1, Data: "a"},
		{Term: 1, Data: "b"},
		{Term: 2, Data: "c"},
	}
	for _, entry := range entries {
		log.Append(entry)
	}

	log.Truncate(1)
	if log.Len() != 1 {
		t.Errorf("Len() after truncate = %d, want 1", log.Len())
	}

	entry, err := log.Get(0)
	if err != nil {
		t.Fatalf("Get(0) returned error: %v", err)
	}
	if entry != entries[0] {
		t.Errorf("Get(0) = %v, want %v", entry, entries[0])
	}
}

func TestConcurrentAccess(t *testing.T) {
	log := NewLog()
	var wg sync.WaitGroup
	workers := 10
	entriesPerWorker := 100

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for j := 0; j < entriesPerWorker; j++ {
				entry := LogEntry{
					Term: uint64(workerID),
					Data: string(rune(j)),
				}
				log.Append(entry)
				time.Sleep(time.Duration(rand.Intn(10)) * time.Millisecond)
			}
		}(i)
	}

	wg.Wait()

	if log.Len() != workers*entriesPerWorker {
		t.Errorf("Expected %d entries, got %d", workers*entriesPerWorker, log.Len())
	}
}

func TestSimulateFailure(t *testing.T) {
	log := NewLog()
	stop := make(chan struct{})
	defer close(stop)

	// Start with some initial entries
	for i := 0; i < 10; i++ {
		log.Append(LogEntry{Term: 1, Data: string(rune(i))})
	}

	// Simulate 50% failure rate
	SimulateFailure(log, 50, stop)

	// Try to append 100 entries
	successCount := 0
	for i := 0; i < 100; i++ {
		if log.Append(LogEntry{Term: 1, Data: string(rune(i))}) == nil {
			successCount++
		}
	}

	// We expect roughly 50% success rate
	if successCount < 40 || successCount > 60 {
		t.Errorf("Unexpected success count: %d, expected ~50", successCount)
	}
}