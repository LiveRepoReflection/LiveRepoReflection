const { MeetingScheduler } = require('../src/meeting_scheduler');

// Dummy implementation for getEmployeeRank for testing purposes.
// Assume that a higher numerical value indicates a higher rank.
const dummyGetEmployeeRank = (employeeId) => {
  // For testing, valid employee IDs are 1 to 1000000.
  // If employeeId is out of this range, return -1 to indicate invalid rank.
  if (employeeId < 1 || employeeId > 1000000) {
    return -1;
  }
  return employeeId;
};

describe('MeetingScheduler', () => {
  let scheduler;

  beforeEach(() => {
    // Create a fresh instance for each test.
    scheduler = new MeetingScheduler(dummyGetEmployeeRank);
  });

  test('schedules a meeting successfully when all employees are available', () => {
    const employeeIds = [1, 2, 3];
    const duration = 60; // in minutes
    const priority = 'High';
    const timeRange = { start: new Date('2023-10-10T09:00:00'), end: new Date('2023-10-10T17:00:00') };
    
    // Attempt to schedule a meeting; calendars are assumed to be initially free.
    const startTime = scheduler.scheduleMeeting({ employeeIds, duration, priority, timeRange });
    expect(startTime).not.toBeNull();
    
    // Verify that the scheduled meeting start time falls within the provided time range.
    const scheduledTime = new Date(startTime).getTime();
    expect(scheduledTime).toBeGreaterThanOrEqual(timeRange.start.getTime());
    expect(scheduledTime + duration * 60000).toBeLessThanOrEqual(timeRange.end.getTime());
  });

  test('returns null when no common time slot is available', () => {
    const employeeIds = [4, 5];
    const duration = 120; // in minutes
    const priority = 'Medium';
    const timeRange = { start: new Date('2023-10-11T09:00:00'), end: new Date('2023-10-11T10:00:00') };

    // Pre-block the entire time range for these employees.
    scheduler.blockTimeForEmployees(employeeIds, { start: new Date('2023-10-11T09:00:00'), end: new Date('2023-10-11T10:00:00') });
    
    const startTime = scheduler.scheduleMeeting({ employeeIds, duration, priority, timeRange });
    expect(startTime).toBeNull();
  });

  test('reschedules a meeting successfully with new parameters', () => {
    const employeeIds = [6, 7];
    const duration = 30;
    const priority = 'High';
    const timeRange = { start: new Date('2023-10-12T10:00:00'), end: new Date('2023-10-12T12:00:00') };

    // Schedule an initial meeting.
    const originalStartTime = scheduler.scheduleMeeting({ employeeIds, duration, priority, timeRange });
    expect(originalStartTime).not.toBeNull();
    
    // Retrieve the meeting ID of the last scheduled meeting.
    const meetingId = scheduler.getLastScheduledMeetingId();
    
    // New meeting request parameters.
    const newEmployeeIds = [6, 7, 8];
    const newDuration = 45;
    const newPriority = 'Medium';
    const newTimeRange = { start: new Date('2023-10-12T13:00:00'), end: new Date('2023-10-12T15:00:00') };

    const newStartTime = scheduler.rescheduleMeeting({
      meetingId,
      employeeIds: newEmployeeIds,
      duration: newDuration,
      priority: newPriority,
      timeRange: newTimeRange,
    });
    expect(newStartTime).not.toBeNull();
    
    // Verify that the new scheduled time falls within the new time range.
    const scheduledTime = new Date(newStartTime).getTime();
    expect(scheduledTime).toBeGreaterThanOrEqual(newTimeRange.start.getTime());
    expect(scheduledTime + newDuration * 60000).toBeLessThanOrEqual(newTimeRange.end.getTime());
  });

  test('reschedule fails with an invalid meeting ID', () => {
    const invalidMeetingId = 'non-existent-id';
    const newStartTime = scheduler.rescheduleMeeting({
      meetingId: invalidMeetingId,
      employeeIds: [1, 2],
      duration: 30,
      priority: 'Low',
      timeRange: { start: new Date('2023-10-13T09:00:00'), end: new Date('2023-10-13T10:00:00') },
    });
    expect(newStartTime).toBeNull();
  });

  test('cancels a meeting successfully', () => {
    const employeeIds = [9, 10];
    const duration = 90;
    const priority = 'High';
    const timeRange = { start: new Date('2023-10-14T08:00:00'), end: new Date('2023-10-14T12:00:00') };

    const startTime = scheduler.scheduleMeeting({ employeeIds, duration, priority, timeRange });
    expect(startTime).not.toBeNull();
    
    const meetingId = scheduler.getLastScheduledMeetingId();
    
    const canceled = scheduler.cancelMeeting(meetingId);
    expect(canceled).toBe(true);
    
    // Attempt to reschedule the cancelled meeting should fail.
    const newStartTime = scheduler.rescheduleMeeting({
      meetingId,
      employeeIds,
      duration,
      priority,
      timeRange,
    });
    expect(newStartTime).toBeNull();
  });

  test('handles overlapping meeting requests appropriately', () => {
    const employeeIds = [11, 12];
    const priority = 'Medium';
    const timeRange = { start: new Date('2023-10-15T09:00:00'), end: new Date('2023-10-15T17:00:00') };

    // Schedule first meeting.
    const startTime1 = scheduler.scheduleMeeting({ employeeIds, duration: 60, priority, timeRange });
    expect(startTime1).not.toBeNull();
    
    // Schedule second meeting; the scheduler should avoid overlapping with the first meeting.
    const startTime2 = scheduler.scheduleMeeting({ employeeIds, duration: 60, priority, timeRange });
    expect(startTime2).not.toBeNull();
    
    const time1 = new Date(startTime1).getTime();
    const time2 = new Date(startTime2).getTime();
    
    // Ensure the two meetings do not overlap.
    expect(Math.abs(time1 - time2)).toBeGreaterThanOrEqual(60 * 60000);
  });

  test('returns null when scheduling with invalid employee IDs', () => {
    const employeeIds = [1000001, 1000002]; // IDs out of valid range
    const duration = 30;
    const priority = 'Low';
    const timeRange = { start: new Date('2023-10-16T10:00:00'), end: new Date('2023-10-16T11:00:00') };

    const startTime = scheduler.scheduleMeeting({ employeeIds, duration, priority, timeRange });
    expect(startTime).toBeNull();
  });
});