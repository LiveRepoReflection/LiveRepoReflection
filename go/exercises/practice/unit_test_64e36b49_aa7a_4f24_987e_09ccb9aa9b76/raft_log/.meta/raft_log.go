package raft_log

import (
	"errors"
	"math/rand"
	"sync"
)

type LogEntry struct {
	Term uint64
	Data string
}

type Log struct {
	entries []LogEntry
	mu      sync.RWMutex
	dropPct int
}

func NewLog() *Log {
	return &Log{
		entries: make([]LogEntry, 0),
	}
}

func (l *Log) Append(entry LogEntry) error {
	l.mu.Lock()
	defer l.mu.Unlock()

	// Simulate random failure if drop percentage is set
	if l.dropPct > 0 && rand.Intn(100) < l.dropPct {
		return errors.New("simulated network failure")
	}

	l.entries = append(l.entries, entry)
	return nil
}

func (l *Log) Get(index int) (LogEntry, error) {
	l.mu.RLock()
	defer l.mu.RUnlock()

	if index < 0 || index >= len(l.entries) {
		return LogEntry{}, errors.New("index out of bounds")
	}
	return l.entries[index], nil
}

func (l *Log) Len() int {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return len(l.entries)
}

func (l *Log) Truncate(index int) {
	l.mu.Lock()
	defer l.mu.Unlock()

	if index < 0 || index >= len(l.entries) {
		return
	}
	l.entries = l.entries[:index]
}

func ConsistencyCheck(leader, follower *Log) int {
	leader.mu.RLock()
	follower.mu.RLock()
	defer leader.mu.RUnlock()
	defer follower.mu.RUnlock()

	minLen := len(leader.entries)
	if len(follower.entries) < minLen {
		minLen = len(follower.entries)
	}

	for i := 0; i < minLen; i++ {
		if leader.entries[i] != follower.entries[i] {
			return i - 1
		}
	}

	if minLen == 0 {
		return -1
	}
	return minLen - 1
}

func SimulateFailure(log *Log, dropPct int, stop <-chan struct{}) {
	log.mu.Lock()
	log.dropPct = dropPct
	log.mu.Unlock()

	go func() {
		<-stop
		log.mu.Lock()
		log.dropPct = 0
		log.mu.Unlock()
	}()
}