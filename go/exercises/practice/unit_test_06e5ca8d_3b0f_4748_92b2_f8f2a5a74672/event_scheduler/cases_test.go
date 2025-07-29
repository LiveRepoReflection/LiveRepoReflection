package event_scheduler

// This file contains test cases for the event scheduler

import (
	"time"
)

type scheduleTestCase struct {
	description   string
	eventID       string
	executionTime int64
	payload       string
	expectedError bool
}

type cancelTestCase struct {
	description   string
	eventID       string
	expectedError bool
}

type getNextEventsTestCase struct {
	description   string
	currentTime   int64
	limit         int
	expectedIDs   []string
	expectedError bool
}

type markExecutedTestCase struct {
	description   string
	eventID       string
	expectedError bool
}

var scheduleTestCases = []scheduleTestCase{
	{
		description:   "Schedule a valid event",
		eventID:       "event1",
		executionTime: time.Now().Add(time.Hour).Unix(),
		payload:       "test payload",
		expectedError: false,
	},
	{
		description:   "Schedule an event with past time",
		eventID:       "event2",
		executionTime: time.Now().Add(-time.Hour).Unix(),
		payload:       "test payload",
		expectedError: true,
	},
	{
		description:   "Schedule an event with duplicate ID",
		eventID:       "event1", // Same as the first test
		executionTime: time.Now().Add(2 * time.Hour).Unix(),
		payload:       "duplicate payload",
		expectedError: false, // Should be idempotent
	},
	{
		description:   "Schedule an event with empty ID",
		eventID:       "",
		executionTime: time.Now().Add(time.Hour).Unix(),
		payload:       "test payload",
		expectedError: true,
	},
}

var cancelTestCases = []cancelTestCase{
	{
		description:   "Cancel an existing event",
		eventID:       "event1",
		expectedError: false,
	},
	{
		description:   "Cancel a non-existent event",
		eventID:       "nonexistent",
		expectedError: true,
	},
	{
		description:   "Cancel with empty ID",
		eventID:       "",
		expectedError: true,
	},
}

// Note: The expected IDs for getNextEventsTestCases would depend on the
// state of the scheduler, which is determined by the test execution order.
// These will be constructed dynamically in the tests.
var getNextEventsTestCases = []getNextEventsTestCase{
	{
		description:   "Get next events with valid time and limit",
		currentTime:   0, // Will be set in the test
		limit:         10,
		expectedIDs:   nil, // Will be set in the test
		expectedError: false,
	},
	{
		description:   "Get next events with zero limit",
		currentTime:   0, // Will be set in the test
		limit:         0,
		expectedIDs:   []string{},
		expectedError: false,
	},
	{
		description:   "Get next events with negative limit",
		currentTime:   0, // Will be set in the test
		limit:         -1,
		expectedIDs:   nil,
		expectedError: true,
	},
	{
		description:   "Get next events with future time",
		currentTime:   0, // Will be set in the test to a future time
		limit:         10,
		expectedIDs:   nil, // Will be set in the test
		expectedError: false,
	},
}

var markExecutedTestCases = []markExecutedTestCase{
	{
		description:   "Mark an existing event as executed",
		eventID:       "event1",
		expectedError: false,
	},
	{
		description:   "Mark a non-existent event as executed",
		eventID:       "nonexistent",
		expectedError: true,
	},
	{
		description:   "Mark with empty ID",
		eventID:       "",
		expectedError: true,
	},
}