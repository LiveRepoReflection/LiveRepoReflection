package sensor_aggregate

type Coordinator struct {
	windowStart       int64
	windowEnd         int64
	globalAggregation map[string]int
}

func NewCoordinator(windowStart, windowEnd int64) *Coordinator {
	return &Coordinator{
		windowStart:       windowStart,
		windowEnd:         windowEnd,
		globalAggregation: make(map[string]int),
	}
}

func (c *Coordinator) ReceivePartialAggregation(partial map[string]int) {
	for key, value := range partial {
		c.globalAggregation[key] += value
	}
}

func (c *Coordinator) GetAggregation() map[string]int {
	return c.globalAggregation
}