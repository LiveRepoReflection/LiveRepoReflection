package traffic_routing

type Edge struct {
	From     int
	To       int
	Capacity int
	Flow     int
}

type Request struct {
	Source    int
	Dest      int
	Demand    int
}

type PathFlow struct {
	Path []int
	Flow int
}