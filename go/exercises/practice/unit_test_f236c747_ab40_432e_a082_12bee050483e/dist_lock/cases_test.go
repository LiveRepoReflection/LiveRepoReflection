package distlock

import "time"

var testCases = []struct {
	description     string
	operations     []operation
	expectedResults []result
}{
	{
		description: "basic lock acquire and release",
		operations: []operation{
			{opType: acquire, resourceID: "resource1", leaseDuration: time.Second},
			{opType: release, resourceID: "resource1"},
		},
		expectedResults: []result{
			{success: true, err: nil},
			{success: true, err: nil},
		},
	},
	{
		description: "concurrent lock attempts",
		operations: []operation{
			{opType: acquire, resourceID: "resource1", leaseDuration: time.Second},
			{opType: acquire, resourceID: "resource1", leaseDuration: time.Second},
			{opType: release, resourceID: "resource1"},
		},
		expectedResults: []result{
			{success: true, err: nil},
			{success: false, err: nil},
			{success: true, err: nil},
		},
	},
	{
		description: "extend lock lease",
		operations: []operation{
			{opType: acquire, resourceID: "resource1", leaseDuration: time.Second},
			{opType: extend, resourceID: "resource1", leaseDuration: time.Second * 2},
			{opType: release, resourceID: "resource1"},
		},
		expectedResults: []result{
			{success: true, err: nil},
			{success: true, err: nil},
			{success: true, err: nil},
		},
	},
	{
		description: "extend non-existent lock",
		operations: []operation{
			{opType: extend, resourceID: "resource1", leaseDuration: time.Second},
		},
		expectedResults: []result{
			{success: false, err: nil},
		},
	},
	{
		description: "release non-existent lock",
		operations: []operation{
			{opType: release, resourceID: "resource1"},
		},
		expectedResults: []result{
			{success: false, err: errLockNotHeld},
		},
	},
	{
		description: "multiple resources",
		operations: []operation{
			{opType: acquire, resourceID: "resource1", leaseDuration: time.Second},
			{opType: acquire, resourceID: "resource2", leaseDuration: time.Second},
			{opType: release, resourceID: "resource1"},
			{opType: release, resourceID: "resource2"},
		},
		expectedResults: []result{
			{success: true, err: nil},
			{success: true, err: nil},
			{success: true, err: nil},
			{success: true, err: nil},
		},
	},
}