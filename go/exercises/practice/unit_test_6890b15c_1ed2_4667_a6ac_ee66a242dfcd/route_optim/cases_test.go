package routeoptim

type Edge struct {
	From int
	To   int
	Cost int
}

type DeliveryRequest struct {
	Start    int
	End      int
	Deadline int64
}

type RouteOptimizer interface {
	ProcessRequest(request DeliveryRequest) bool
}