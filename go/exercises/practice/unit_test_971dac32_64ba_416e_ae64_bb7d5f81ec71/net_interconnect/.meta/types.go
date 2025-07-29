package network

// FaultyLink represents a faulty link in the network
// Type can be "input", "middle", or "output"
// id1 and id2 depend on the type:
// - "input": id1 is input switch ID, id2 is middle switch ID
// - "middle": id1 is middle switch ID, id2 is output switch ID
// - "output": id1 is output switch ID, id2 is server ID
type FaultyLink struct {
	Type string
	ID1  int
	ID2  int
}