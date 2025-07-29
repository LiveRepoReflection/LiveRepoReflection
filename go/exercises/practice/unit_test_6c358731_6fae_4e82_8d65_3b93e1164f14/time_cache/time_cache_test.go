package time_cache

import (
	"testing"
	"time"
)

func TestTimeCache(t *testing.T) {
	t.Run("basic set and get operations", func(t *testing.T) {
		tc := NewTimeCache()
		now := int(time.Now().Unix())

		tc.Set("key1", "value1", now)
		tc.Set("key1", "value2", now+1)
		tc.Set("key2", "value3", now+2)

		if val := tc.Get("key1", now); val != "value1" {
			t.Errorf("Expected value1, got %s", val)
		}
		if val := tc.Get("key1", now+1); val != "value2" {
			t.Errorf("Expected value2, got %s", val)
		}
		if val := tc.Get("key2", now+2); val != "value3" {
			t.Errorf("Expected value3, got %s", val)
		}
	})

	t.Run("get with non-existent key", func(t *testing.T) {
		tc := NewTimeCache()
		now := int(time.Now().Unix())

		if val := tc.Get("nonexistent", now); val != "" {
			t.Errorf("Expected empty string, got %s", val)
		}
	})

	t.Run("get with timestamp before any entry", func(t *testing.T) {
		tc := NewTimeCache()
		now := int(time.Now().Unix())

		tc.Set("key1", "value1", now+1)
		if val := tc.Get("key1", now); val != "" {
			t.Errorf("Expected empty string, got %s", val)
		}
	})

	t.Run("count operation", func(t *testing.T) {
		tc := NewTimeCache()
		now := int(time.Now().Unix())

		tc.Set("key1", "value1", now)
		tc.Set("key1", "value2", now+1)
		tc.Set("key1", "value3", now+2)
		tc.Set("key2", "value4", now+3)

		if count := tc.Count("key1", now, now+2); count != 3 {
			t.Errorf("Expected count 3, got %d", count)
		}
		if count := tc.Count("key1", now+1, now+1); count != 1 {
			t.Errorf("Expected count 1, got %d", count)
		}
		if count := tc.Count("key2", now, now+3); count != 1 {
			t.Errorf("Expected count 1, got %d", count)
		}
	})

	t.Run("eviction operation", func(t *testing.T) {
		tc := NewTimeCache()
		now := int(time.Now().Unix())

		// Each entry: key (3) + value (6) = 9 bytes
		tc.Set("key", "value1", now)
		tc.Set("key", "value2", now+1)
		tc.Set("key", "value3", now+2)

		// Should keep only the newest entry (value3)
		tc.Evict(9)

		if count := tc.Count("key", now, now+2); count != 1 {
			t.Errorf("Expected count 1 after eviction, got %d", count)
		}
		if val := tc.Get("key", now+2); val != "value3" {
			t.Errorf("Expected value3 to remain after eviction, got %s", val)
		}
	})

	t.Run("concurrent operations", func(t *testing.T) {
		tc := NewTimeCache()
		now := int(time.Now().Unix())
		done := make(chan bool)

		go func() {
			tc.Set("key1", "value1", now)
			tc.Set("key1", "value2", now+1)
			done <- true
		}()

		go func() {
			tc.Set("key2", "value3", now+2)
			tc.Set("key2", "value4", now+3)
			done <- true
		}()

		<-done
		<-done

		if val := tc.Get("key1", now+1); val != "value2" {
			t.Errorf("Expected value2, got %s", val)
		}
		if val := tc.Get("key2", now+3); val != "value4" {
			t.Errorf("Expected value4, got %s", val)
		}
	})
}