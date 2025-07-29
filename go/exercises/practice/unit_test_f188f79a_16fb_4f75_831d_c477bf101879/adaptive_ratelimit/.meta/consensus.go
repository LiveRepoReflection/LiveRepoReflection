package ratelimit

import (
	"context"
	"sync"
	"time"
)

type consensusManager struct {
	mu            sync.RWMutex
	lastConsensus time.Time
	nodes         map[string]*nodeState
}

type nodeState struct {
	lastSeen time.Time
	counter  int64
}

func newConsensusManager() *consensusManager {
	return &consensusManager{
		nodes: make(map[string]*nodeState),
	}
}

func (cm *consensusManager) recordConsensus(node string, counter int64) {
	cm.mu.Lock()
	defer cm.mu.Unlock()

	if _, exists := cm.nodes[node]; !exists {
		cm.nodes[node] = &nodeState{}
	}

	cm.nodes[node].lastSeen = time.Now()
	cm.nodes[node].counter = counter
	cm.lastConsensus = time.Now()
}

func (cm *consensusManager) isNodeHealthy(node string) bool {
	cm.mu.RLock()
	defer cm.mu.RUnlock()

	state, exists := cm.nodes[node]
	if !exists {
		return false
	}

	return time.Since(state.lastSeen) < 5*time.Second
}

func (cm *consensusManager) cleanupStaleNodes(ctx context.Context) {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			cm.mu.Lock()
			now := time.Now()
			for node, state := range cm.nodes {
				if now.Sub(state.lastSeen) > 10*time.Second {
					delete(cm.nodes, node)
				}
			}
			cm.mu.Unlock()
		}
	}
}