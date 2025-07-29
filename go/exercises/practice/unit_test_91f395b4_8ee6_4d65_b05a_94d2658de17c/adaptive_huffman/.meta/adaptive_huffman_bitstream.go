package adaptive_huffman

// BitStream provides utilities for working with streams of bits
type BitStream struct {
	data     []byte
	position int // Position in bits
}

// NewBitStream creates a new BitStream
func NewBitStream() *BitStream {
	return &BitStream{
		data:     make([]byte, 0),
		position: 0,
	}
}

// WriteBit appends a single bit to the BitStream
func (bs *BitStream) WriteBit(bit byte) {
	bytePos := bs.position / 8
	bitPos := bs.position % 8
	
	// Ensure we have enough space
	if bytePos >= len(bs.data) {
		bs.data = append(bs.data, 0)
	}
	
	// Set the bit
	if bit == 1 {
		bs.data[bytePos] |= (1 << uint(7-bitPos))
	}
	
	bs.position++
}

// WriteBytes appends multiple bits (represented as a byte slice) to the BitStream
func (bs *BitStream) WriteBytes(bytes []byte) {
	for _, b := range bytes {
		bs.WriteBit(b)
	}
}

// WriteByte appends a byte (8 bits) to the BitStream
func (bs *BitStream) WriteByte(b byte) {
	for i := 7; i >= 0; i-- {
		bit := (b >> uint(i)) & 1
		bs.WriteBit(bit)
	}
}

// ReadBit reads a single bit from the BitStream
func (bs *BitStream) ReadBit() (byte, bool) {
	bytePos := bs.position / 8
	bitPos := bs.position % 8
	
	if bytePos >= len(bs.data) {
		return 0, false
	}
	
	bit := (bs.data[bytePos] >> uint(7-bitPos)) & 1
	bs.position++
	
	return bit, true
}

// ReadByte reads 8 bits from the BitStream as a byte
func (bs *BitStream) ReadByte() (byte, bool) {
	var b byte
	for i := 0; i < 8; i++ {
		bit, ok := bs.ReadBit()
		if !ok {
			return 0, false
		}
		b = (b << 1) | bit
	}
	return b, true
}

// ToBytes converts the BitStream to a byte slice
func (bs *BitStream) ToBytes() []byte {
	// Calculate how many full bytes we have
	numBytes := (bs.position + 7) / 8
	
	// Make sure we don't return more bytes than we have
	if numBytes > len(bs.data) {
		numBytes = len(bs.data)
	}
	
	return bs.data[:numBytes]
}

// ToBitString converts the BitStream to a string of '0's and '1's
func (bs *BitStream) ToBitString() string {
	var result []byte
	originalPosition := bs.position
	
	// Reset position to read from the beginning
	bs.position = 0
	
	for i := 0; i < originalPosition; i++ {
		bit, _ := bs.ReadBit()
		if bit == 0 {
			result = append(result, '0')
		} else {
			result = append(result, '1')
		}
	}
	
	// Restore the original position
	bs.position = originalPosition
	
	return string(result)
}

// FromBitString converts a string of '0's and '1's to a BitStream
func FromBitString(s string) *BitStream {
	bs := NewBitStream()
	for _, c := range s {
		if c == '0' {
			bs.WriteBit(0)
		} else if c == '1' {
			bs.WriteBit(1)
		}
	}
	return bs
}