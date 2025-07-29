package collaborative_map

import (
	"sync"
	"testing"
	"time"
)

func TestMapService(t *testing.T) {
	t.Run("basic single claim", func(t *testing.T) {
		service := NewMapService(10)
		claim := Claim{
			Row:       1,
			Col:       2,
			Value:     "test",
			Timestamp: time.Now().UnixNano(),
			UserID:    "user1",
		}
		service.SubmitClaim(claim)
		value := service.GetValue(1, 2)
		if value != "test" {
			t.Errorf("expected 'test', got '%s'", value)
		}
	})

	t.Run("last write wins", func(t *testing.T) {
		service := NewMapService(10)
		claim1 := Claim{
			Row:       1,
			Col:       1,
			Value:     "old",
			Timestamp: 100,
			UserID:    "user1",
		}
		claim2 := Claim{
			Row:       1,
			Col:       1,
			Value:     "new",
			Timestamp: 200,
			UserID:    "user2",
		}
		service.SubmitClaim(claim1)
		service.SubmitClaim(claim2)
		value := service.GetValue(1, 1)
		if value != "new" {
			t.Errorf("expected 'new', got '%s'", value)
		}
	})

	t.Run("tiebreaker with userID", func(t *testing.T) {
		service := NewMapService(10)
		claim1 := Claim{
			Row:       2,
			Col:       2,
			Value:     "apple",
			Timestamp: 100,
			UserID:    "userB",
		}
		claim2 := Claim{
			Row:       2,
			Col:       2,
			Value:     "banana",
			Timestamp: 100,
			UserID:    "userA",
		}
		service.SubmitClaim(claim1)
		service.SubmitClaim(claim2)
		value := service.GetValue(2, 2)
		if value != "banana" {
			t.Errorf("expected 'banana', got '%s'", value)
		}
	})

	t.Run("concurrent claims", func(t *testing.T) {
		service := NewMapService(100)
		var wg sync.WaitGroup
		for i := 0; i < 100; i++ {
			wg.Add(1)
			go func(i int) {
				defer wg.Done()
				claim := Claim{
					Row:       0,
					Col:       0,
					Value:     "value",
					Timestamp: int64(i),
					UserID:    "user",
				}
				service.SubmitClaim(claim)
			}(i)
		}
		wg.Wait()
		value := service.GetValue(0, 0)
		if value != "value" {
			t.Errorf("expected 'value', got '%s'", value)
		}
	})

	t.Run("invalid coordinates", func(t *testing.T) {
		service := NewMapService(5)
		claim := Claim{
			Row:       10,
			Col:       10,
			Value:     "invalid",
			Timestamp: 100,
			UserID:    "user",
		}
		service.SubmitClaim(claim)
		value := service.GetValue(10, 10)
		if value != "" {
			t.Errorf("expected empty string, got '%s'", value)
		}
	})

	t.Run("size check", func(t *testing.T) {
		service := NewMapService(15)
		if service.Size() != 15 {
			t.Errorf("expected size 15, got %d", service.Size())
		}
	})
}

func BenchmarkMapService(b *testing.B) {
	service := NewMapService(1000)
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		claim := Claim{
			Row:       i % 1000,
			Col:       i % 1000,
			Value:     "value",
			Timestamp: int64(i),
			UserID:    "user",
		}
		service.SubmitClaim(claim)
		_ = service.GetValue(i%1000, i%1000)
	}
}