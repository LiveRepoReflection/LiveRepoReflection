package adaptive_huffman

// This file contains additional test cases for the adaptive Huffman compression algorithm

var testCases = []struct {
	description string
	input       string
	// We don't provide expected compressed output since the exact bitstream may vary
	// based on implementation details. Instead, we'll verify correctness by
	// ensuring that decompression works properly.
}{
	{
		description: "empty string",
		input:       "",
	},
	{
		description: "single character",
		input:       "a",
	},
	{
		description: "repeated single character",
		input:       "aaaaa",
	},
	{
		description: "two distinct characters",
		input:       "ab",
	},
	{
		description: "repeated pattern",
		input:       "ababab",
	},
	{
		description: "simple sentence",
		input:       "hello world",
	},
	{
		description: "characters with varying frequencies",
		input:       "the quick brown fox jumps over the lazy dog",
	},
	{
		description: "all lowercase letters",
		input:       "abcdefghijklmnopqrstuvwxyz",
	},
	{
		description: "uppercase and lowercase",
		input:       "AbCdEfGhIjKlMnOpQrStUvWxYz",
	},
	{
		description: "alphanumeric characters",
		input:       "a1b2c3d4e5f6g7h8i9j0",
	},
	{
		description: "special characters",
		input:       "!@#$%^&*()_+-=[]{}|;':,./<>?",
	},
	{
		description: "repeated blocks",
		input:       "abcabcabc123123123",
	},
	{
		description: "paragraph of text",
		input:       "This is a longer paragraph of text that contains various words, punctuation, and symbols. It should provide a more realistic test case for the adaptive Huffman algorithm by having a natural distribution of characters that might be encountered in typical English text.",
	},
	{
		description: "characters appearing in reverse frequency order",
		input:       "zzzzyyyyxxxwwwvvvuuutttsssrrr",
	},
	{
		description: "binary data representation",
		input:       "\x00\x01\x02\x03\x04\x05\xFF\xFE\xFD\xFC",
	},
}