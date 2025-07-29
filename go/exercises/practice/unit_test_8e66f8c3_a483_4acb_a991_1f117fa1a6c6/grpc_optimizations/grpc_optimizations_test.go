package grpc_optimizations

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"
)

type mockGRPCService struct {
	calls     int
	callMutex sync.Mutex
}

func (m *mockGRPCService) GetUserProfile(ctx context.Context, userIDs []string) (map[string]*UserProfile, error) {
	m.callMutex.Lock()
	m.calls++
	m.callMutex.Unlock()

	result := make(map[string]*UserProfile)
	for _, id := range userIDs {
		result[id] = &UserProfile{
			ID:   id,
			Name: fmt.Sprintf("User %s", id),
		}
	}
	return result, nil
}

func TestCaching(t *testing.T) {
	mock := &mockGRPCService{}
	client := NewGRPCClient(mock, ClientConfig{
		CacheSize:    100,
		CacheTTL:     time.Second,
		MaxBatchSize: 10,
		MaxDelay:     time.Millisecond * 50,
	})

	// Test basic caching
	t.Run("Basic Cache Hit", func(t *testing.T) {
		profile, err := client.GetUserProfile(context.Background(), "user1")
		if err != nil {
			t.Fatalf("First call failed: %v", err)
		}
		if profile.ID != "user1" {
			t.Errorf("Wrong profile returned")
		}

		initialCalls := mock.calls
		profile, err = client.GetUserProfile(context.Background(), "user1")
		if err != nil {
			t.Fatalf("Second call failed: %v", err)
		}
		if mock.calls != initialCalls {
			t.Error("Cache miss: service was called again")
		}
	})

	// Test cache eviction
	t.Run("Cache Eviction", func(t *testing.T) {
		client = NewGRPCClient(mock, ClientConfig{
			CacheSize: 2,
			CacheTTL:  time.Second,
		})

		// Fill cache
		_, _ = client.GetUserProfile(context.Background(), "user1")
		_, _ = client.GetUserProfile(context.Background(), "user2")
		initialCalls := mock.calls

		// This should evict user1
		_, _ = client.GetUserProfile(context.Background(), "user3")

		// This should miss
		_, _ = client.GetUserProfile(context.Background(), "user1")
		if mock.calls <= initialCalls {
			t.Error("Cache wasn't evicted")
		}
	})
}

func TestBatching(t *testing.T) {
	mock := &mockGRPCService{}
	client := NewGRPCClient(mock, ClientConfig{
		MaxBatchSize: 3,
		MaxDelay:     time.Millisecond * 50,
	})

	t.Run("Request Batching", func(t *testing.T) {
		var wg sync.WaitGroup
		initialCalls := mock.calls

		// Make concurrent requests
		for i := 0; i < 6; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				_, err := client.GetUserProfile(context.Background(), fmt.Sprintf("user%d", id))
				if err != nil {
					t.Errorf("Request failed: %v", err)
				}
			}(i)
		}

		wg.Wait()

		// Should have made 2 batched calls (6 requests / batch size of 3)
		expectedCalls := initialCalls + 2
		if mock.calls != expectedCalls {
			t.Errorf("Expected %d calls, got %d", expectedCalls, mock.calls)
		}
	})
}

func TestErrorHandling(t *testing.T) {
	errorMock := &mockGRPCService{}
	client := NewGRPCClient(errorMock, ClientConfig{
		MaxRetries:    3,
		RetryInterval: time.Millisecond,
	})

	t.Run("Context Cancellation", func(t *testing.T) {
		ctx, cancel := context.WithCancel(context.Background())
		cancel()

		_, err := client.GetUserProfile(ctx, "user1")
		if err == nil {
			t.Error("Expected error due to cancelled context")
		}
	})

	t.Run("Invalid Input", func(t *testing.T) {
		_, err := client.GetUserProfile(context.Background(), "")
		if err == nil {
			t.Error("Expected error for empty user ID")
		}
	})
}

func TestConcurrency(t *testing.T) {
	mock := &mockGRPCService{}
	client := NewGRPCClient(mock, ClientConfig{
		CacheSize:    1000,
		MaxBatchSize: 10,
		MaxDelay:     time.Millisecond * 50,
	})

	t.Run("Concurrent Requests", func(t *testing.T) {
		var wg sync.WaitGroup
		concurrent := 100

		for i := 0; i < concurrent; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				_, err := client.GetUserProfile(context.Background(), fmt.Sprintf("user%d", id))
				if err != nil {
					t.Errorf("Concurrent request failed: %v", err)
				}
			}(i)
		}

		wg.Wait()
	})
}

func BenchmarkGRPCClient(b *testing.B) {
	mock := &mockGRPCService{}
	client := NewGRPCClient(mock, ClientConfig{
		CacheSize:    1000,
		MaxBatchSize: 10,
		MaxDelay:     time.Millisecond * 50,
	})

	b.Run("Sequential", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			_, _ = client.GetUserProfile(context.Background(), fmt.Sprintf("user%d", i))
		}
	})

	b.Run("Concurrent", func(b *testing.B) {
		b.RunParallel(func(pb *testing.PB) {
			i := 0
			for pb.Next() {
				_, _ = client.GetUserProfile(context.Background(), fmt.Sprintf("user%d", i))
				i++
			}
		})
	})
}