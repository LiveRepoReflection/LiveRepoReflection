package ride_share

type Edge struct {
	Destination int
	Time       int
}

type RideRequest struct {
	Start         int
	Destination   int
	PickupTime    int64
	DropoffLimit  int64
	Passengers    int
}

type Vehicle struct {
	Location  int
	Capacity  int
}

type RideAssignment struct {
	RideIndex   int
	VehicleIndex int
}