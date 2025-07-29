'use strict';

class MeetingScheduler {
  constructor(getEmployeeRank) {
    this.getEmployeeRank = getEmployeeRank;
    this.calendars = new Map(); // Map of employeeId -> array of busy intervals { start, end, meetingId }
    this.meetings = new Map(); // Map of meetingId -> meeting object { meetingId, employeeIds, start, duration, priority, requestOrder }
    this.meetingCounter = 1;
    this.lastMeetingId = null;
  }

  // Helper: Get or create the calendar for an employee.
  _getCalendar(employeeId) {
    if (!this.calendars.has(employeeId)) {
      this.calendars.set(employeeId, []);
    }
    return this.calendars.get(employeeId);
  }

  // Helper: Add a busy interval to an employee's calendar.
  _addBusyInterval(employeeId, interval) {
    const calendar = this._getCalendar(employeeId);
    calendar.push(interval);
    calendar.sort((a, b) => a.start - b.start);
  }

  // Helper: Remove a busy interval associated with a meetingId from an employee's calendar.
  _removeBusyInterval(employeeId, meetingId) {
    const calendar = this._getCalendar(employeeId);
    const newCal = calendar.filter(interval => interval.meetingId !== meetingId);
    this.calendars.set(employeeId, newCal);
  }

  // Helper: Compute free intervals for an employee between a given time range.
  _computeFreeIntervals(employeeId, timeRange) {
    const calendar = this._getCalendar(employeeId);
    const freeIntervals = [];
    let currentStart = new Date(timeRange.start.getTime());
    for (const interval of calendar) {
      // Skip intervals that end before the time range.
      if (interval.end <= timeRange.start) continue;
      // If an interval starts after the requested range, break early.
      if (interval.start >= timeRange.end) break;
      if (interval.start > currentStart) {
        freeIntervals.push({
          start: new Date(currentStart.getTime()),
          end: new Date(Math.min(interval.start.getTime(), timeRange.end.getTime()))
        });
      }
      if (interval.end > currentStart) {
        currentStart = new Date(interval.end.getTime());
      }
      if (currentStart >= timeRange.end) break;
    }
    if (currentStart < timeRange.end) {
      freeIntervals.push({
        start: new Date(currentStart.getTime()),
        end: new Date(timeRange.end.getTime())
      });
    }
    return freeIntervals;
  }

  // Helper: Intersect two lists of intervals.
  _intersectIntervals(list1, list2) {
    let i = 0, j = 0;
    const intersections = [];
    while (i < list1.length && j < list2.length) {
      const a = list1[i];
      const b = list2[j];
      const start = new Date(Math.max(a.start.getTime(), b.start.getTime()));
      const end = new Date(Math.min(a.end.getTime(), b.end.getTime()));
      if (start < end) {
        intersections.push({ start, end });
      }
      if (a.end < b.end) {
        i++;
      } else {
        j++;
      }
    }
    return intersections;
  }

  // Helper: Calculate common free intervals across multiple employees for the given time range.
  _getCommonFreeIntervals(employeeIds, timeRange) {
    let common = this._computeFreeIntervals(employeeIds[0], timeRange);
    for (let k = 1; k < employeeIds.length; k++) {
      const freeIntervals = this._computeFreeIntervals(employeeIds[k], timeRange);
      common = this._intersectIntervals(common, freeIntervals);
      if (common.length === 0) break;
    }
    return common;
  }

  // Internal method to schedule a meeting. If meetingId is provided, it will be used; otherwise, a new meeting is created.
  _internalScheduleMeeting({ employeeIds, duration, priority, timeRange, meetingId }) {
    // Validate employee IDs.
    for (const emp of employeeIds) {
      if (this.getEmployeeRank(emp) < 0) {
        return null;
      }
    }
    const durationMs = duration * 60000;
    const commonIntervals = this._getCommonFreeIntervals(employeeIds, timeRange);
    let chosenStart = null;
    for (const interval of commonIntervals) {
      if ((interval.end.getTime() - interval.start.getTime()) >= durationMs) {
        chosenStart = new Date(interval.start.getTime());
        break;
      }
    }
    if (chosenStart === null) {
      return null;
    }
    const meetingInterval = {
      start: chosenStart,
      end: new Date(chosenStart.getTime() + durationMs),
      meetingId: meetingId
    };
    for (const emp of employeeIds) {
      this._addBusyInterval(emp, meetingInterval);
    }
    return chosenStart;
  }

  scheduleMeeting({ employeeIds, duration, priority, timeRange }) {
    const meetingId = `M${this.meetingCounter}`;
    const scheduledStart = this._internalScheduleMeeting({ employeeIds, duration, priority, timeRange, meetingId });
    if (scheduledStart === null) {
      return null;
    }
    const meeting = {
      meetingId,
      employeeIds,
      start: scheduledStart,
      duration,
      priority,
      requestOrder: this.meetingCounter
    };
    this.meetings.set(meetingId, meeting);
    this.lastMeetingId = meetingId;
    this.meetingCounter++;
    return scheduledStart.toISOString();
  }

  rescheduleMeeting({ meetingId, employeeIds, duration, priority, timeRange }) {
    if (!this.meetings.has(meetingId)) {
      return null;
    }
    const oldMeeting = this.meetings.get(meetingId);
    // Remove the old meeting intervals from the calendars.
    for (const emp of oldMeeting.employeeIds) {
      this._removeBusyInterval(emp, meetingId);
    }
    const scheduledStart = this._internalScheduleMeeting({ employeeIds, duration, priority, timeRange, meetingId });
    if (scheduledStart === null) {
      // Rescheduling fails; do not restore the original meeting.
      this.meetings.delete(meetingId);
      return null;
    }
    const updatedMeeting = {
      meetingId,
      employeeIds,
      start: scheduledStart,
      duration,
      priority,
      requestOrder: oldMeeting.requestOrder
    };
    this.meetings.set(meetingId, updatedMeeting);
    return scheduledStart.toISOString();
  }

  cancelMeeting(meetingId) {
    if (!this.meetings.has(meetingId)) {
      return false;
    }
    const meeting = this.meetings.get(meetingId);
    for (const emp of meeting.employeeIds) {
      this._removeBusyInterval(emp, meetingId);
    }
    this.meetings.delete(meetingId);
    return true;
  }

  blockTimeForEmployees(employeeIds, interval) {
    // interval is an object: { start: Date, end: Date }
    for (const emp of employeeIds) {
      const busyInterval = {
        start: new Date(interval.start.getTime()),
        end: new Date(interval.end.getTime()),
        meetingId: `BLOCK_${Date.now()}_${Math.random()}`
      };
      this._addBusyInterval(emp, busyInterval);
    }
  }

  getLastScheduledMeetingId() {
    return this.lastMeetingId;
  }
}

module.exports = {
  MeetingScheduler
};