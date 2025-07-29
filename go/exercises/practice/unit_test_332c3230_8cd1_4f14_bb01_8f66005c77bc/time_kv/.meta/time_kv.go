package time_kv

import (
	"sort"
	"sync"
)

type TimeValue struct {
	Value     string
	Timestamp int64
	NodeID    int
}

type TimeKVStore struct {
	data map[string][]TimeValue
	mu   sync.RWMutex
}

func NewTimeKVStore() *TimeKVStore {
	return &TimeKVStore{
		data: make(map[string][]TimeValue),
	}
}

func (s *TimeKVStore) Set(key string, value string, timestamp int64) {
	s.SetWithNodeID(key, value, timestamp, 0)
}

func (s *TimeKVStore) SetWithNodeID(key string, value string, timestamp int64, nodeID int) {
	s.mu.Lock()
	defer s.mu.Unlock()

	tv := TimeValue{
		Value:     value,
		Timestamp: timestamp,
		NodeID:    nodeID,
	}

	values := s.data[key]
	index := sort.Search(len(values), func(i int) bool {
		if values[i].Timestamp == timestamp {
			return values[i].NodeID <= nodeID
		}
		return values[i].Timestamp >= timestamp
	})

	if index < len(values) && values[index].Timestamp == timestamp {
		if values[index].NodeID < nodeID {
			values[index] = tv
		}
	} else {
		s.data[key] = append(values[:index], append([]TimeValue{tv}, values[index:]...)...)
	}
}

func (s *TimeKVStore) Get(key string, timestamp int64) string {
	s.mu.RLock()
	defer s.mu.RUnlock()

	values, exists := s.data[key]
	if !exists {
		return ""
	}

	index := sort.Search(len(values), func(i int) bool {
		return values[i].Timestamp > timestamp
	})

	if index == 0 {
		return ""
	}
	return values[index-1].Value
}

func (s *TimeKVStore) MultiGet(keys []string, timestamp int64) map[string]string {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make(map[string]string)
	for _, key := range keys {
		result[key] = s.Get(key, timestamp)
	}
	return result
}

func (s *TimeKVStore) RangeGet(key string, startTime int64, endTime int64) []TimeValue {
	s.mu.RLock()
	defer s.mu.RUnlock()

	values, exists := s.data[key]
	if !exists {
		return nil
	}

	startIndex := sort.Search(len(values), func(i int) bool {
		return values[i].Timestamp >= startTime
	})

	endIndex := sort.Search(len(values), func(i int) bool {
		return values[i].Timestamp > endTime
	})

	if startIndex >= endIndex {
		return nil
	}

	result := make([]TimeValue, endIndex-startIndex)
	copy(result, values[startIndex:endIndex])
	return result
}