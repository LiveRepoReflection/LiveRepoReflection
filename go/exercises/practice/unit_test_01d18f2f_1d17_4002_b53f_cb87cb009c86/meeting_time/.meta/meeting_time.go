package meetingtime

// OptimalMeetingScheduler finds the earliest possible meeting time slot
func OptimalMeetingScheduler(graph map[int][]int, busyCalendars map[int][][]int64, 
	requiredAttendees []int, meetingDuration int, availabilityWindowStart, availabilityWindowEnd int64) []int64 {
	
	if len(requiredAttendees) == 0 || int64(meetingDuration) > availabilityWindowEnd-availabilityWindowStart {
		return []int64{}
	}

	// Get all attendees including those in the reporting chain
	allRequiredAttendees := make(map[int]bool)
	for _, attendee := range requiredAttendees {
		if !getAllRequiredAttendees(graph, attendee, allRequiredAttendees) {
			return []int64{} // If any required attendee is not in the graph
		}
	}

	// Merge all busy calendars
	mergedBusySlots := make([][]int64, 0)
	for attendee := range allRequiredAttendees {
		if slots, exists := busyCalendars[attendee]; exists {
			mergedBusySlots = mergeBusySlots(mergedBusySlots, slots)
		}
	}

	// Find the earliest available slot
	return findEarliestSlot(mergedBusySlots, int64(meetingDuration), availabilityWindowStart, availabilityWindowEnd)
}

// getAllRequiredAttendees traverses the graph to get all attendees in the reporting chain
func getAllRequiredAttendees(graph map[int][]int, current int, visited map[int]bool) bool {
	if _, exists := graph[current]; !exists {
		return false
	}

	visited[current] = true
	for _, manager := range graph[current] {
		if !visited[manager] {
			if !getAllRequiredAttendees(graph, manager, visited) {
				return false
			}
		}
	}
	return true
}

// mergeBusySlots merges two lists of busy time slots
func mergeBusySlots(slots1, slots2 [][]int64) [][]int64 {
	if len(slots1) == 0 {
		return slots2
	}
	if len(slots2) == 0 {
		return slots1
	}

	merged := make([][]int64, 0)
	i, j := 0, 0

	for i < len(slots1) || j < len(slots2) {
		var current []int64
		if i >= len(slots1) {
			current = slots2[j]
			j++
		} else if j >= len(slots2) {
			current = slots1[i]
			i++
		} else if slots1[i][0] <= slots2[j][0] {
			current = slots1[i]
			i++
		} else {
			current = slots2[j]
			j++
		}

		if len(merged) == 0 || merged[len(merged)-1][1] < current[0] {
			merged = append(merged, current)
		} else {
			// Merge overlapping slots
			if current[1] > merged[len(merged)-1][1] {
				merged[len(merged)-1][1] = current[1]
			}
		}
	}

	return merged
}

// findEarliestSlot finds the earliest available time slot of required duration
func findEarliestSlot(busySlots [][]int64, duration, windowStart, windowEnd int64) []int64 {
	currentTime := windowStart

	for _, slot := range busySlots {
		if currentTime+duration <= slot[0] {
			return []int64{currentTime, currentTime + duration}
		}
		currentTime = slot[1]
	}

	if currentTime+duration <= windowEnd {
		return []int64{currentTime, currentTime + duration}
	}

	return []int64{}
}