package keyval_store

import (
	"encoding/gob"
	"os"
	"sort"
	"sync"
)

type KeyValue struct {
	Key   string
	Value string
}

type KeyValStore struct {
	data  map[string]string
	mutex sync.RWMutex
}

func NewKeyValStore() *KeyValStore {
	return &KeyValStore{
		data: make(map[string]string),
	}
}

func (s *KeyValStore) Put(key string, value string) {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.data[key] = value
}

func (s *KeyValStore) Get(key string) string {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	return s.data[key]
}

func (s *KeyValStore) Delete(key string) {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	delete(s.data, key)
}

func (s *KeyValStore) Range(startKey string, endKey string) []KeyValue {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	var results []KeyValue
	var keys []string

	for k := range s.data {
		if k >= startKey && k < endKey {
			keys = append(keys, k)
		}
	}

	sort.Strings(keys)

	for _, k := range keys {
		results = append(results, KeyValue{Key: k, Value: s.data[k]})
	}

	return results
}

func (s *KeyValStore) Count(startKey string, endKey string) int {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	count := 0
	for k := range s.data {
		if k >= startKey && k < endKey {
			count++
		}
	}
	return count
}

func (s *KeyValStore) Backup(filepath string) error {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	file, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer file.Close()

	encoder := gob.NewEncoder(file)
	return encoder.Encode(s.data)
}

func (s *KeyValStore) Restore(filepath string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	file, err := os.Open(filepath)
	if err != nil {
		return err
	}
	defer file.Close()

	decoder := gob.NewDecoder(file)
	return decoder.Decode(&s.data)
}