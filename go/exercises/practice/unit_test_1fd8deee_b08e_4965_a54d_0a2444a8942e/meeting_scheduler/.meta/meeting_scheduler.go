package meetingscheduler

import (
	"sort"
)

type meetingRequest struct {
	request      MeetingRequest
	possibleLocs map[int]bool // possible office locations
	scheduled    bool
}

// ScheduleMeetings implements the meeting scheduler algorithm
func ScheduleMeetings(employees []Employee, offices []Office, requests []MeetingRequest) []ScheduledMeeting {
	// Create employee and office maps for quick lookup
	employeeMap := make(map[int]*Employee)
	for i := range employees {
		employeeMap[employees[i].EmployeeID] = &employees[i]
	}

	officeMap := make(map[int]*Office)
	for i := range offices {
		officeMap[offices[i].OfficeID] = &offices[i]
	}

	// Create room availability tracker for each office
	roomAvailability := make(map[int][]int) // officeID -> timeslot -> rooms available
	for _, office := range offices {
		roomAvailability[office.OfficeID] = make([]int, len(employees[0].Schedule))
		for i := range roomAvailability[office.OfficeID] {
			roomAvailability[office.OfficeID][i] = office.Capacity
		}
	}

	// Sort meeting requests by priority (highest first)
	sortedRequests := make([]meetingRequest, len(requests))
	for i, req := range requests {
		sortedRequests[i] = meetingRequest{
			request:      req,
			possibleLocs: make(map[int]bool),
			scheduled:    false,
		}
	}
	sort.Slice(sortedRequests, func(i, j int) bool {
		return sortedRequests[i].request.Priority > sortedRequests[j].request.Priority
	})

	result := make([]ScheduledMeeting, 0)

	// Process each meeting request
	for i := range sortedRequests {
		req := &sortedRequests[i]
		
		// Find all possible office locations
		officeFreq := make(map[int]int)
		for _, attendeeID := range req.request.Attendees {
			employee := employeeMap[attendeeID]
			officeFreq[employee.OfficeID]++
		}

		// Try each possible time slot
		bestOffice := -1
		bestStartSlot := -1
		minCommunicationCost := len(offices) + 1

		for _, startSlot := range req.request.TimeSlotOptions {
			if startSlot+req.request.Duration > len(employees[0].Schedule) {
				continue
			}

			// Check attendee availability
			for _, attendeeID := range req.request.Attendees {
				employee := employeeMap[attendeeID]
				available := true
				for slot := startSlot; slot < startSlot+req.request.Duration; slot++ {
					if employee.Schedule[slot] {
						available = false
						break
					}
				}
				if !available {
					goto nextTimeSlot
				}
			}

			// Try each possible office
			for officeID := range officeFreq {
				// Check room availability
				available := true
				for slot := startSlot; slot < startSlot+req.request.Duration; slot++ {
					if roomAvailability[officeID][slot] <= 0 {
						available = false
						break
					}
				}

				if available {
					// Calculate communication cost (number of different offices involved)
					communicationCost := len(officeFreq)
					
					if communicationCost < minCommunicationCost {
						minCommunicationCost = communicationCost
						bestOffice = officeID
						bestStartSlot = startSlot
					}
				}
			}
			
		nextTimeSlot:
		}

		// If a valid slot was found, schedule the meeting
		if bestOffice != -1 {
			// Update room availability
			for slot := bestStartSlot; slot < bestStartSlot+req.request.Duration; slot++ {
				roomAvailability[bestOffice][slot]--
			}

			// Mark attendees as busy
			for _, attendeeID := range req.request.Attendees {
				employee := employeeMap[attendeeID]
				for slot := bestStartSlot; slot < bestStartSlot+req.request.Duration; slot++ {
					employee.Schedule[slot] = true
				}
			}

			result = append(result, ScheduledMeeting{
				MeetingID:     req.request.MeetingID,
				OfficeID:      bestOffice,
				StartTimeSlot: bestStartSlot,
			})
		}
	}

	// Sort result by MeetingID for consistent output
	sort.Slice(result, func(i, j int) bool {
		return result[i].MeetingID < result[j].MeetingID
	})

	return result
}