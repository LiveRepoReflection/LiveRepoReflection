package meetingtime

import (
	"reflect"
	"testing"
)

func TestOptimalMeetingScheduler(t *testing.T) {
	tests := []struct {
		name                   string
		graph                  map[int][]int
		busyCalendars         map[int][][]int64
		requiredAttendees     []int
		meetingDuration       int
		availabilityWindowStart int64
		availabilityWindowEnd   int64
		want                  []int64
	}{
		{
			name: "Simple case - one attendee with one busy slot",
			graph: map[int][]int{
				1: {2},
				2: {},
			},
			busyCalendars: map[int][][]int64{
				1: {{100, 200}},
			},
			requiredAttendees:      []int{1},
			meetingDuration:        50,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   300,
			want:                   []int64{0, 50},
		},
		{
			name: "Multiple attendees with overlapping busy slots",
			graph: map[int][]int{
				1: {3},
				2: {3},
				3: {},
			},
			busyCalendars: map[int][][]int64{
				1: {{100, 200}},
				2: {{150, 250}},
				3: {{175, 225}},
			},
			requiredAttendees:      []int{1, 2},
			meetingDuration:        60,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   300,
			want:                   []int64{0, 60},
		},
		{
			name: "No available slot within window",
			graph: map[int][]int{
				1: {},
			},
			busyCalendars: map[int][][]int64{
				1: {{0, 100}},
			},
			requiredAttendees:      []int{1},
			meetingDuration:        30,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   50,
			want:                   []int64{},
		},
		{
			name: "Meeting duration longer than window",
			graph: map[int][]int{
				1: {},
			},
			busyCalendars: map[int][][]int64{
				1: {},
			},
			requiredAttendees:      []int{1},
			meetingDuration:        100,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   50,
			want:                   []int64{},
		},
		{
			name: "Empty required attendees",
			graph: map[int][]int{
				1: {},
			},
			busyCalendars:         map[int][][]int64{},
			requiredAttendees:     []int{},
			meetingDuration:       30,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   100,
			want:                  []int64{},
		},
		{
			name: "Complex hierarchy with multiple busy slots",
			graph: map[int][]int{
				1: {4},
				2: {4},
				3: {5},
				4: {6},
				5: {6},
				6: {},
			},
			busyCalendars: map[int][][]int64{
				1: {{100, 200}},
				2: {{150, 250}},
				3: {{200, 300}},
				4: {{400, 500}},
				5: {{450, 550}},
				6: {{600, 700}},
			},
			requiredAttendees:      []int{1, 2, 3},
			meetingDuration:        50,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   800,
			want:                   []int64{0, 50},
		},
		{
			name: "Non-existent employee in required attendees",
			graph: map[int][]int{
				1: {},
			},
			busyCalendars: map[int][][]int64{
				1: {},
			},
			requiredAttendees:      []int{1, 999},
			meetingDuration:        30,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   100,
			want:                   []int64{},
		},
		{
			name: "Employee with no calendar entry",
			graph: map[int][]int{
				1: {},
				2: {},
			},
			busyCalendars: map[int][][]int64{
				1: {{100, 200}},
			},
			requiredAttendees:      []int{1, 2},
			meetingDuration:        50,
			availabilityWindowStart: 0,
			availabilityWindowEnd:   300,
			want:                   []int64{0, 50},
		},
		{
			name: "Tight scheduling between busy slots",
			graph: map[int][]int{
				1: {},
			},
			busyCalendars: map[int][][]int64{
				1: {{100, 200}, {250, 350}},
			},
			requiredAttendees:      []int{1},
			meetingDuration:        30,
			availabilityWindowStart: 150,
			availabilityWindowEnd:   300,
			want:                   []int64{200, 230},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalMeetingScheduler(
				tt.graph,
				tt.busyCalendars,
				tt.requiredAttendees,
				tt.meetingDuration,
				tt.availabilityWindowStart,
				tt.availabilityWindowEnd,
			)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("OptimalMeetingScheduler() = %v, want %v", got, tt.want)
			}
		})
	}
}