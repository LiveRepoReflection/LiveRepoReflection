package keyval_store

import "testing"

func BenchmarkPut(b *testing.B) {
	store := NewKeyValStore()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		store.Put("bench_key", "bench_value")
	}
}

func BenchmarkGet(b *testing.B) {
	store := NewKeyValStore()
	store.Put("bench_key", "bench_value")
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		store.Get("bench_key")
	}
}

func BenchmarkRange(b *testing.B) {
	store := NewKeyValStore()
	for i := 0; i < 1000; i++ {
		store.Put(string(rune(i)), "value")
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		store.Range("a", "z")
	}
}

func BenchmarkCount(b *testing.B) {
	store := NewKeyValStore()
	for i := 0; i < 1000; i++ {
		store.Put(string(rune(i)), "value")
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		store.Count("a", "z")
	}
}