package meetingscheduler

import (
	"reflect"
	"testing"
)

type Employee struct {
	EmployeeID int
	OfficeID   int
	Schedule   []bool // true for busy, false for free
}

type Office struct {
	OfficeID  int
	Capacity  int
}

type MeetingRequest struct {
	MeetingID        int
	Attendees        []int
	Duration         int
	TimeSlotOptions  []int
	Priority         int
}

type ScheduledMeeting struct {
	MeetingID     int
	OfficeID      int
	StartTimeSlot int
}

func TestMeetingScheduler(t *testing.T) {
	tests := []struct {
		name            string
		employees       []Employee
		offices        []Office
		meetingRequests []MeetingRequest
		want           []ScheduledMeeting
	}{
		{
			name: "Simple case - one meeting, two employees, same office",
			employees: []Employee{
				{
					EmployeeID: 1,
					OfficeID:   1,
					Schedule:   []bool{false, false, false, false}, // all slots free
				},
				{
					EmployeeID: 2,
					OfficeID:   1,
					Schedule:   []bool{false, false, false, false}, // all slots free
				},
			},
			offices: []Office{
				{
					OfficeID:  1,
					Capacity:  1,
				},
			},
			meetingRequests: []MeetingRequest{
				{
					MeetingID:       1,
					Attendees:       []int{1, 2},
					Duration:        2,
					TimeSlotOptions: []int{0, 1},
					Priority:        1,
				},
			},
			want: []ScheduledMeeting{
				{
					MeetingID:     1,
					OfficeID:      1,
					StartTimeSlot: 0,
				},
			},
		},
		{
			name: "Complex case - multiple meetings, different offices",
			employees: []Employee{
				{
					EmployeeID: 1,
					OfficeID:   1,
					Schedule:   []bool{true, false, false, false},
				},
				{
					EmployeeID: 2,
					OfficeID:   2,
					Schedule:   []bool{false, true, false, false},
				},
				{
					EmployeeID: 3,
					OfficeID:   1,
					Schedule:   []bool{false, false, true, false},
				},
			},
			offices: []Office{
				{
					OfficeID:  1,
					Capacity:  2,
				},
				{
					OfficeID:  2,
					Capacity:  1,
				},
			},
			meetingRequests: []MeetingRequest{
				{
					MeetingID:       1,
					Attendees:       []int{1, 2},
					Duration:        1,
					TimeSlotOptions: []int{2},
					Priority:        2,
				},
				{
					MeetingID:       2,
					Attendees:       []int{2, 3},
					Duration:        1,
					TimeSlotOptions: []int{0},
					Priority:        1,
				},
			},
			want: []ScheduledMeeting{
				{
					MeetingID:     1,
					OfficeID:      1,
					StartTimeSlot: 2,
				},
				{
					MeetingID:     2,
					OfficeID:      2,
					StartTimeSlot: 0,
				},
			},
		},
		{
			name: "Impossible case - no available slots",
			employees: []Employee{
				{
					EmployeeID: 1,
					OfficeID:   1,
					Schedule:   []bool{true, true, true, true},
				},
			},
			offices: []Office{
				{
					OfficeID:  1,
					Capacity:  1,
				},
			},
			meetingRequests: []MeetingRequest{
				{
					MeetingID:       1,
					Attendees:       []int{1},
					Duration:        1,
					TimeSlotOptions: []int{0, 1, 2, 3},
					Priority:        1,
				},
			},
			want: []ScheduledMeeting{},
		},
		{
			name: "Priority test - higher priority should be scheduled first",
			employees: []Employee{
				{
					EmployeeID: 1,
					OfficeID:   1,
					Schedule:   []bool{false, false, false, false},
				},
				{
					EmployeeID: 2,
					OfficeID:   1,
					Schedule:   []bool{false, false, false, false},
				},
			},
			offices: []Office{
				{
					OfficeID:  1,
					Capacity:  1,
				},
			},
			meetingRequests: []MeetingRequest{
				{
					MeetingID:       1,
					Attendees:       []int{1},
					Duration:        4,
					TimeSlotOptions: []int{0},
					Priority:        1,
				},
				{
					MeetingID:       2,
					Attendees:       []int{2},
					Duration:        1,
					TimeSlotOptions: []int{0},
					Priority:        2,
				},
			},
			want: []ScheduledMeeting{
				{
					MeetingID:     2,
					OfficeID:      1,
					StartTimeSlot: 0,
				},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := ScheduleMeetings(tt.employees, tt.offices, tt.meetingRequests)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("ScheduleMeetings() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMeetingScheduler(b *testing.B) {
	employees := make([]Employee, 1000)
	for i := range employees {
		schedule := make([]bool, 48)
		employees[i] = Employee{
			EmployeeID: i,
			OfficeID:   i % 10,
			Schedule:   schedule,
		}
	}

	offices := make([]Office, 10)
	for i := range offices {
		offices[i] = Office{
			OfficeID:  i,
			Capacity:  5,
		}
	}

	meetingRequests := make([]MeetingRequest, 100)
	for i := range meetingRequests {
		attendees := make([]int, 5)
		for j := range attendees {
			attendees[j] = j + (i * 5)
		}
		timeSlots := make([]int, 5)
		for j := range timeSlots {
			timeSlots[j] = j * 2
		}
		meetingRequests[i] = MeetingRequest{
			MeetingID:       i,
			Attendees:       attendees,
			Duration:        2,
			TimeSlotOptions: timeSlots,
			Priority:        i % 5,
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ScheduleMeetings(employees, offices, meetingRequests)
	}
}