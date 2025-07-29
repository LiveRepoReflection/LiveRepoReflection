import unittest
import random
import string
from adaptive_huffman import encode, decode

class TestAdaptiveHuffman(unittest.TestCase):
    def test_empty_string(self):
        input_str = ""
        encoded = encode(input_str)
        decoded = decode(encoded)
        self.assertEqual(decoded, input_str)
    
    def test_single_character(self):
        input_str = "A"
        encoded = encode(input_str)
        decoded = decode(encoded)
        self.assertEqual(decoded, input_str)

    def test_repeated_character(self):
        input_str = "AAAAAA"
        encoded = encode(input_str)
        decoded = decode(encoded)
        self.assertEqual(decoded, input_str)
    
    def test_multiple_unique_characters(self):
        input_str = "ABCABCXYZ"
        encoded = encode(input_str)
        decoded = decode(encoded)
        self.assertEqual(decoded, input_str)
    
    def test_mixed_content(self):
        input_str = "The quick brown fox jumps over the lazy dog! 1234567890"
        encoded = encode(input_str)
        decoded = decode(encoded)
        self.assertEqual(decoded, input_str)

    def test_long_random_string(self):
        # Generate a random string of length 10000 using ASCII printable characters.
        input_str = ''.join(random.choices(string.printable[:-6], k=10000))
        encoded = encode(input_str)
        decoded = decode(encoded)
        self.assertEqual(decoded, input_str)

    def test_encoding_decoding_consistency(self):
        # Multiple iterations with different random strings to test consistency
        for _ in range(5):
            length = random.randint(100, 1000)
            input_str = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + ' ', k=length))
            encoded = encode(input_str)
            decoded = decode(encoded)
            self.assertEqual(decoded, input_str)

if __name__ == '__main__':
    unittest.main()