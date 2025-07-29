import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import java.time.LocalDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class MeetingSchedulerTest {

    private LocalDateTime horizonStart;
    private LocalDateTime horizonEnd;
    private List<Integer> employees;
    private List<Integer> rooms;

    @BeforeEach
    public void setup() {
        // Define a scheduling horizon from Oct 1, 2023 09:00 to Oct 1, 2023 17:00
        horizonStart = LocalDateTime.of(2023, 10, 1, 9, 0);
        horizonEnd = LocalDateTime.of(2023, 10, 1, 17, 0);
        // Use four employees
        employees = Arrays.asList(1, 2, 3, 4);
        // Meeting room capacities available
        rooms = Arrays.asList(3, 5, 10);
    }

    @Test
    public void testMeetingScheduledDuringWorkHours() {
        int duration = 60; // meeting duration in minutes
        int minimumAttendance = 3;

        // Create employee data map
        Map<Integer, Map<String, Object>> employeeData = new HashMap<>();

        // Employee 1: Busy from 10:00 to 11:00, meeting cost 5
        Map<String, Object> emp1 = new HashMap<>();
        emp1.put("meetingCost", 5);
        List<LocalDateTime[]> busySlots1 = new ArrayList<>();
        busySlots1.add(new LocalDateTime[]{LocalDateTime.of(2023, 10, 1, 10, 0), LocalDateTime.of(2023, 10, 1, 11, 0)});
        emp1.put("busySlots", busySlots1);
        employeeData.put(1, emp1);

        // Employee 2: Busy from 12:00 to 13:00, meeting cost 10
        Map<String, Object> emp2 = new HashMap<>();
        emp2.put("meetingCost", 10);
        List<LocalDateTime[]> busySlots2 = new ArrayList<>();
        busySlots2.add(new LocalDateTime[]{LocalDateTime.of(2023, 10, 1, 12, 0), LocalDateTime.of(2023, 10, 1, 13, 0)});
        emp2.put("busySlots", busySlots2);
        employeeData.put(2, emp2);

        // Employee 3: Busy from 14:00 to 15:00, meeting cost 8
        Map<String, Object> emp3 = new HashMap<>();
        emp3.put("meetingCost", 8);
        List<LocalDateTime[]> busySlots3 = new ArrayList<>();
        busySlots3.add(new LocalDateTime[]{LocalDateTime.of(2023, 10, 1, 14, 0), LocalDateTime.of(2023, 10, 1, 15, 0)});
        emp3.put("busySlots", busySlots3);
        employeeData.put(3, emp3);

        // Employee 4: No busy slots, meeting cost 7
        Map<String, Object> emp4 = new HashMap<>();
        emp4.put("meetingCost", 7);
        List<LocalDateTime[]> busySlots4 = new ArrayList<>();
        emp4.put("busySlots", busySlots4);
        employeeData.put(4, emp4);

        // Initialize the MeetingScheduler with the provided data.
        MeetingScheduler scheduler = new MeetingScheduler(
                employees, duration, horizonStart, horizonEnd, minimumAttendance, rooms, employeeData);

        MeetingScheduleResult result = scheduler.scheduleMeeting();

        // Assert that the scheduler found an available meeting time.
        assertNotNull(result, "Expected a valid meeting schedule result.");

        // Validate that the meeting start time lies within the scheduling horizon.
        LocalDateTime meetingStart = result.getMeetingStartTime();
        assertTrue((!meetingStart.isBefore(horizonStart)) && (!meetingStart.plusMinutes(duration).isAfter(horizonEnd)),
                "Meeting should be within the scheduling horizon.");

        // Validate that the chosen room's capacity meets or exceeds the minimum required attendance.
        int roomCapacity = result.getRoomCapacity();
        assertTrue(roomCapacity >= minimumAttendance,
                "The selected meeting room must have capacity for at least the minimum attendance.");
    }

    @Test
    public void testNoAvailableMeetingTime() {
        int duration = 120; // 2-hour meeting
        int minimumAttendance = 3;

        // All employees are busy throughout the entire scheduling horizon.
        Map<Integer, Map<String, Object>> employeeData = new HashMap<>();
        for (Integer id : employees) {
            Map<String, Object> emp = new HashMap<>();
            emp.put("meetingCost", 5);
            List<LocalDateTime[]> busySlots = new ArrayList<>();
            busySlots.add(new LocalDateTime[]{horizonStart, horizonEnd});
            emp.put("busySlots", busySlots);
            employeeData.put(id, emp);
        }

        MeetingScheduler scheduler = new MeetingScheduler(
                employees, duration, horizonStart, horizonEnd, minimumAttendance, rooms, employeeData);

        MeetingScheduleResult result = scheduler.scheduleMeeting();

        // Since all employees are busy, expect no possible meeting time (null result).
        assertNull(result, "Expected no available meeting time due to full schedules.");
    }

    @Test
    public void testMeetingRoomSelection() {
        int duration = 45; // 45-minute meeting
        int minimumAttendance = 2;

        // Create employee data: Only 2 employees can attend, so a smaller room should be chosen.
        Map<Integer, Map<String, Object>> employeeData = new HashMap<>();

        // Employee 1: Free (no busy slots) with meeting cost 3.
        Map<String, Object> emp1 = new HashMap<>();
        emp1.put("meetingCost", 3);
        List<LocalDateTime[]> busySlots1 = new ArrayList<>();
        emp1.put("busySlots", busySlots1);
        employeeData.put(1, emp1);

        // Employee 2: Has one busy slot outside the ideal meeting time.
        Map<String, Object> emp2 = new HashMap<>();
        emp2.put("meetingCost", 4);
        List<LocalDateTime[]> busySlots2 = new ArrayList<>();
        busySlots2.add(new LocalDateTime[]{LocalDateTime.of(2023, 10, 1, 11, 0), LocalDateTime.of(2023, 10, 1, 12, 0)});
        emp2.put("busySlots", busySlots2);
        employeeData.put(2, emp2);

        // Employee 3: Busy during most of the horizon.
        Map<String, Object> emp3 = new HashMap<>();
        emp3.put("meetingCost", 6);
        List<LocalDateTime[]> busySlots3 = new ArrayList<>();
        busySlots3.add(new LocalDateTime[]{horizonStart, horizonEnd});
        emp3.put("busySlots", busySlots3);
        employeeData.put(3, emp3);

        // Employee 4: Free (no busy slots) with meeting cost 2.
        Map<String, Object> emp4 = new HashMap<>();
        emp4.put("meetingCost", 2);
        List<LocalDateTime[]> busySlots4 = new ArrayList<>();
        emp4.put("busySlots", busySlots4);
        employeeData.put(4, emp4);

        MeetingScheduler scheduler = new MeetingScheduler(
                employees, duration, horizonStart, horizonEnd, minimumAttendance, rooms, employeeData);

        MeetingScheduleResult result = scheduler.scheduleMeeting();

        // Validate that meeting is scheduled and room capacity is minimal for meeting at least 2 attendees.
        assertNotNull(result, "Expected a valid meeting schedule result.");
        int selectedRoomCapacity = result.getRoomCapacity();
        // Among provided rooms (3, 5, 10), for 2 attendees the optimal room would be 3.
        assertEquals(3, selectedRoomCapacity, "The scheduler should select the smallest room that fits the attendees.");
    }

    @Test
    public void testMeetingAtEdgeOfHorizon() {
        int duration = 30; // 30-minute meeting
        int minimumAttendance = 2;

        // Adjust scheduling horizon to a narrow time window.
        LocalDateTime narrowStart = LocalDateTime.of(2023, 10, 1, 16, 30);
        LocalDateTime narrowEnd = LocalDateTime.of(2023, 10, 1, 17, 0);

        Map<Integer, Map<String, Object>> employeeData = new HashMap<>();
        // Employees are free in the narrow window.
        for (Integer id : employees) {
            Map<String, Object> emp = new HashMap<>();
            emp.put("meetingCost", 5);
            List<LocalDateTime[]> busySlots = new ArrayList<>();
            // Busy before the narrow window to simulate free period.
            busySlots.add(new LocalDateTime[]{LocalDateTime.of(2023, 10, 1, 9, 0), LocalDateTime.of(2023, 10, 1, 16, 0)});
            emp.put("busySlots", busySlots);
            employeeData.put(id, emp);
        }

        MeetingScheduler scheduler = new MeetingScheduler(
                employees, duration, narrowStart, narrowEnd, minimumAttendance, rooms, employeeData);

        MeetingScheduleResult result = scheduler.scheduleMeeting();

        // The meeting should start exactly at the narrow start and finish within the horizon.
        assertNotNull(result, "Expected a valid meeting schedule result.");
        LocalDateTime meetingStart = result.getMeetingStartTime();
        assertEquals(narrowStart, meetingStart, "Meeting should be scheduled at the start of the narrow horizon.");

        // Ensure that the meeting does not exceed the scheduling horizon.
        assertFalse(meetingStart.plusMinutes(duration).isAfter(narrowEnd),
                "The meeting should end within the scheduling horizon.");
    }
}