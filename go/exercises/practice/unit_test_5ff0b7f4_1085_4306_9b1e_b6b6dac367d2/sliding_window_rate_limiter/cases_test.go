package sliding_window_rate_limiter

import "time"

var testCases = []struct {
	description    string
	requestLimit   int
	windowSize     time.Duration
	clientID       string
	requests       []time.Time
	expectedAllow  bool
}{
	{
		description:    "single request within limit",
		requestLimit:   10,
		windowSize:     time.Minute,
		clientID:       "client1",
		requests:       []time.Time{time.Now()},
		expectedAllow:  true,
	},
	{
		description:    "multiple requests at limit",
		requestLimit:   2,
		windowSize:     time.Minute,
		clientID:       "client2",
		requests: []time.Time{
			time.Now(),
			time.Now().Add(time.Second * 10),
			time.Now().Add(time.Second * 20),
		},
		expectedAllow:  false,
	},
	{
		description:    "requests after window expiration",
		requestLimit:   1,
		windowSize:     time.Second,
		clientID:       "client3",
		requests: []time.Time{
			time.Now(),
			time.Now().Add(time.Second * 2),
		},
		expectedAllow:  true,
	},
}