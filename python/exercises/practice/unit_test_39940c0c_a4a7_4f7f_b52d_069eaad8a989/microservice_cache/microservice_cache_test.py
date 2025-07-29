import unittest
from microservice_cache import process_queries

class MicroserviceCacheTest(unittest.TestCase):
    def test_basic_queries(self):
        # Test with no eviction needed.
        N = 3
        C = 10
        Q = [
            (0, 1, "hello"),  # len("hello") = 5 -> "olleh"
            (1, 2, "world")   # len("world") = 5 -> "dlrow"
        ]
        expected = ["olleh", "dlrow"]
        result = process_queries(N, C, Q)
        self.assertEqual(result, expected)
    
    def test_cache_hit(self):
        # Test where queries are repeated causing cache hits.
        N = 3
        C = 10
        Q = [
            (0, 1, "hello"),   # cache miss -> "olleh"
            (1, 2, "world"),   # cache miss -> "dlrow"
            (0, 1, "hello"),   # cache hit -> "olleh"
            (1, 2, "world"),   # cache hit -> "dlrow"
        ]
        expected = ["olleh", "dlrow", "olleh", "dlrow"]
        result = process_queries(N, C, Q)
        self.assertEqual(result, expected)

    def test_eviction_policy(self):
        # Test eviction scenario.
        # Initially, cache capacity (C=10) can hold two entries of 5 each.
        # Third query with string "python" (length 6) will force eviction.
        # LRU order should evict the least recently used items until enough space.
        N = 3
        C = 10
        Q = [
            (0, 1, "hello"),   # cache miss, store "hello":5, usage=5 -> result "olleh"
            (1, 2, "world"),   # cache miss, store "world":5, usage=5+5=10 -> result "dlrow"
            (0, 1, "hello"),   # cache hit -> "olleh"
            (2, 0, "python"),  # cache miss, len("python")=6, usage 10+6 > 10:
                               # Evict LRU ("world") first (usage becomes 5), still insufficient: evict next LRU ("hello"), usage becomes 0, add "python" (usage becomes 6)
                               # result -> "nohtyp"
            (1, 2, "world"),   # cache miss because it was evicted, compute -> "dlrow"
        ]
        expected = ["olleh", "dlrow", "olleh", "nohtyp", "dlrow"]
        result = process_queries(N, C, Q)
        self.assertEqual(result, expected)

    def test_item_too_large_for_cache(self):
        # Test when the data length exceeds the cache capacity.
        # Since the item cannot be cached (len(data) > C), each query should be a miss.
        N = 2
        C = 3  # capacity is less than length of "abcd" (4)
        Q = [
            (0, 1, "abcd"),
            (0, 1, "abcd")
        ]
        # Both queries should trigger direct call (reverse of "abcd" is "dcba")
        expected = ["dcba", "dcba"]
        result = process_queries(N, C, Q)
        self.assertEqual(result, expected)

    def test_multiple_evictions(self):
        # Test scenario with multiple evictions in one query addition.
        # Setup queries so that eviction is triggered for multiple items.
        N = 4
        C = 12  # small cache capacity
        Q = [
            (0, 1, "one"),    # len("one")=3 -> "eno"
            (1, 2, "two"),    # len("two")=3 -> "owt"
            (2, 3, "three"),  # len("three")=5 -> "eerht"
            # At this point, usage=3+3+5 = 11, within capacity.
            (3, 0, "four"),   # len("four")=4 -> "ruof", new total=11+4=15 >12.
                               # Eviction: remove LRU until enough space.
                               # LRU order: "one", "two", "three". Remove "one" (usage becomes 11-3=8),
                               # then 8+4=12 exactly, so "one" is evicted, keep others.
            (0, 1, "one")     # Query "one" again: since it was evicted, return reverse.
        ]
        # Expected outputs:
        #  "eno", "owt", "eerht", "ruof", "eno" respectively.
        expected = ["eno", "owt", "eerht", "ruof", "eno"]
        result = process_queries(N, C, Q)
        self.assertEqual(result, expected)

    def test_large_number_of_queries(self):
        # Test performance with a large number of queries.
        N = 10
        C = 1000
        Q = []
        expected = []
        # Create alternating patterns
        for i in range(1000):
            data = "data" + str(i)
            Q.append((i % N, (i+1) % N, data))
            expected.append(data[::-1])
        result = process_queries(N, C, Q)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()