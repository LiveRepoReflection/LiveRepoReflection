package adaptive_huffman

import (
	"strings"
	"testing"
)

func TestAdaptiveHuffmanCompression(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		expected string // This is not the actual expected output, just used for verification
	}{
		{
			name:     "Empty string",
			input:    "",
			expected: "",
		},
		{
			name:     "Single character",
			input:    "a",
			expected: "a",
		},
		{
			name:     "Repeated characters",
			input:    "aaaa",
			expected: "aaaa",
		},
		{
			name:     "Simple string",
			input:    "abcd",
			expected: "abcd",
		},
		{
			name:     "String with repetition",
			input:    "ababcabc",
			expected: "ababcabc",
		},
		{
			name:     "Complex string",
			input:    "the quick brown fox jumps over the lazy dog",
			expected: "the quick brown fox jumps over the lazy dog",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Test compression
			compressed := Compress(tt.input)
			
			// Verify the output is a valid bitstream
			if !isValidBitStream(compressed) {
				t.Errorf("Compress(%q) = %q, not a valid bitstream", tt.input, compressed)
			}

			// Test decompression
			decompressed := Decompress(compressed)
			if decompressed != tt.input {
				t.Errorf("Decompress(Compress(%q)) = %q, want %q", tt.input, decompressed, tt.input)
			}

			// Log compression stats
			if tt.input != "" {
				compressionRatio := float64(len(compressed)) / float64(len(tt.input)*8)
				t.Logf("Input length: %d bits, Compressed length: %d bits, Compression ratio: %.2f", len(tt.input)*8, len(compressed), compressionRatio)
			}
		})
	}
}

func TestLargeInput(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping large input test in short mode")
	}

	// Generate a large input with various patterns
	var sb strings.Builder
	
	// Repetitive pattern
	for i := 0; i < 1000; i++ {
		sb.WriteString("abcdefg")
	}
	
	// Single character repeats
	for i := 0; i < 1000; i++ {
		sb.WriteByte('x')
	}
	
	// Alternating patterns
	for i := 0; i < 1000; i++ {
		sb.WriteString("ab")
	}
	
	largeInput := sb.String()
	
	// Test compression and decompression
	compressed := Compress(largeInput)
	decompressed := Decompress(compressed)
	
	if decompressed != largeInput {
		t.Errorf("Decompression of large input failed. Expected len %d, got len %d", 
			len(largeInput), len(decompressed))
	}
	
	compressionRatio := float64(len(compressed)) / float64(len(largeInput)*8)
	t.Logf("Large input - Original: %d bits, Compressed: %d bits, Ratio: %.2f", 
		len(largeInput)*8, len(compressed), compressionRatio)
}

func TestEdgeCases(t *testing.T) {
	// Test all ASCII characters
	var asciiInput strings.Builder
	for i := 0; i < 256; i++ {
		asciiInput.WriteByte(byte(i))
	}
	
	compressed := Compress(asciiInput.String())
	decompressed := Decompress(compressed)
	
	if decompressed != asciiInput.String() {
		t.Errorf("Decompression of ASCII characters failed")
		
		// Find which characters don't match
		for i := 0; i < len(decompressed) && i < len(asciiInput.String()); i++ {
			if decompressed[i] != asciiInput.String()[i] {
				t.Errorf("Mismatch at position %d: expected %d, got %d", 
					i, asciiInput.String()[i], decompressed[i])
				break
			}
		}
	}
}

func TestRandomOrder(t *testing.T) {
	// Test with characters appearing in random order to test dynamic dictionary expansion
	input := "zyxwvutsrqponmlkjihgfedcba"
	
	compressed := Compress(input)
	decompressed := Decompress(compressed)
	
	if decompressed != input {
		t.Errorf("Random order test failed: expected %q, got %q", input, decompressed)
	}
}

func TestOutputConsistency(t *testing.T) {
	// The output should be consistent for the same input
	input := "hello world"
	
	firstCompression := Compress(input)
	secondCompression := Compress(input)
	
	if firstCompression != secondCompression {
		t.Errorf("Output not consistent for the same input")
	}
}

func isValidBitStream(s string) bool {
	// Check if the string contains only '0' and '1'
	for _, c := range s {
		if c != '0' && c != '1' {
			return false
		}
	}
	return true
}

func BenchmarkCompression(b *testing.B) {
	// Generate a sample text
	var sb strings.Builder
	for i := 0; i < 10000; i++ {
		sb.WriteString("The quick brown fox jumps over the lazy dog. ")
	}
	input := sb.String()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Compress(input)
	}
}

func BenchmarkDecompression(b *testing.B) {
	// Generate a sample text and compress it
	var sb strings.Builder
	for i := 0; i < 10000; i++ {
		sb.WriteString("The quick brown fox jumps over the lazy dog. ")
	}
	input := sb.String()
	compressed := Compress(input)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Decompress(compressed)
	}
}