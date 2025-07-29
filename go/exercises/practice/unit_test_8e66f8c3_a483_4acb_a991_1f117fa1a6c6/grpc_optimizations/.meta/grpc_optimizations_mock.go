package grpc_optimizations

import (
	"context"
	"sync"
)

type MockGRPCService struct {
	mu    sync.Mutex
	calls int
}

func (m *MockGRPCService) GetUserProfile(ctx context.Context, userIDs []string) (map[string]*UserProfile, error) {
	m.mu.Lock()
	m.calls++
	m.mu.Unlock()

	result := make(map[string]*UserProfile)
	for _, id := range userIDs {
		result[id] = &UserProfile{
			ID:   id,
			Name: "Test User",
		}
	}
	return result, nil
}

func (m *MockGRPCService) GetCalls() int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.calls
}