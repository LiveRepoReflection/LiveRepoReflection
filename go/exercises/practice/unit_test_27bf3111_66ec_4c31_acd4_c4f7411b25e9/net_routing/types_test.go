package net_routing

type Connection struct {
	Node1, Node2 int
	Latency      int
}

type Operation struct {
	Type   string
	NodeID int
	Node1  int
	Node2  int
	Latency int
}

type PathQuery struct {
	From, To int
}

type PathResult struct {
	Path    []int
	Latency int
}