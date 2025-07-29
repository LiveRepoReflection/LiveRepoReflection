use std::collections::HashMap;
use std::error::Error;
use std::fmt;

// Custom error type for our meeting scheduler.
#[derive(Debug)]
pub struct SchedulerError(String);

impl fmt::Display for SchedulerError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "SchedulerError: {}", self.0)
    }
}

impl Error for SchedulerError {}

// Data Structures

#[derive(Clone, Debug)]
pub struct RecurrencePattern {
    // For simplicity we use rule as a string. Example: "3rd Wednesday"
    pub rule: String,
    // Exceptions represent months to exclude (e.g., 12 for December)
    pub exceptions: Vec<u32>,
}

#[derive(Clone, Debug)]
pub struct Meeting {
    pub id: u64,
    pub title: String,
    pub organizer: String,
    pub participants: Vec<String>,
    pub start_time: u64, // Using a simple numeric timestamp.
    pub duration: u64,   // duration in minutes.
    pub recurrence: Option<RecurrencePattern>,
}

#[derive(Clone, Debug)]
pub struct MeetingRequest {
    pub title: String,
    pub organizer: String,
    pub participants: Vec<String>,
    pub start_time: u64,
    pub duration: u64,
    pub recurrence: Option<RecurrencePattern>,
}

#[derive(Clone, Debug)]
pub struct Employee {
    pub name: String,
    pub office: String,
}

#[derive(Clone, Debug)]
pub struct Office {
    pub name: String,
    pub timezone_offset: i32, // offset in hours.
    pub employees: Vec<String>,
}

pub struct CalendarSystem {
    offices: HashMap<String, Office>,
    employees: HashMap<String, Employee>,
    meetings: HashMap<u64, Meeting>,
    meeting_counter: u64,
}

impl CalendarSystem {
    pub fn new() -> Self {
        CalendarSystem {
            offices: HashMap::new(),
            employees: HashMap::new(),
            meetings: HashMap::new(),
            meeting_counter: 1,
        }
    }

    pub fn add_office(&mut self, office_name: &str, timezone_offset: i32) {
        let office = Office {
            name: office_name.to_string(),
            timezone_offset,
            employees: Vec::new(),
        };
        self.offices.insert(office_name.to_string(), office);
    }

    pub fn add_employee(&mut self, employee_name: &str, office_name: &str) {
        if let Some(office) = self.offices.get_mut(office_name) {
            office.employees.push(employee_name.to_string());
            let employee = Employee {
                name: employee_name.to_string(),
                office: office_name.to_string(),
            };
            self.employees.insert(employee_name.to_string(), employee);
        }
    }

    // Helper to check if two time intervals overlap.
    fn intervals_overlap(start1: u64, duration1: u64, start2: u64, duration2: u64) -> bool {
        let end1 = start1 + duration1;
        let end2 = start2 + duration2;
        start1 < end2 && start2 < end1
    }

    // Check for conflict for an individual employee
    fn has_conflict(&self, employee: &str, start_time: u64, duration: u64) -> bool {
        for meeting in self.meetings.values() {
            if meeting.organizer == employee || meeting.participants.contains(&employee.to_string()) {
                if Self::intervals_overlap(meeting.start_time, meeting.duration, start_time, duration) {
                    return true;
                }
            }
        }
        false
    }

    pub fn schedule_meeting(&mut self, request: MeetingRequest) -> Result<Meeting, Box<dyn Error>> {
        // Check conflict for organizer and all participants
        let all_people = {
            let mut v = request.participants.clone();
            v.push(request.organizer.clone());
            v
        };
        for person in all_people.iter() {
            if self.has_conflict(person, request.start_time, request.duration) {
                return Err(Box::new(SchedulerError(format!(
                    "Scheduling conflict for {}",
                    person
                ))));
            }
        }
        // Create meeting and assign unique id.
        let meeting = Meeting {
            id: self.meeting_counter,
            title: request.title,
            organizer: request.organizer,
            participants: request.participants,
            start_time: request.start_time,
            duration: request.duration,
            recurrence: request.recurrence,
        };
        self.meetings.insert(self.meeting_counter, meeting.clone());
        self.meeting_counter += 1;
        Ok(meeting)
    }

    // Suggest an alternative time by simply shifting the start_time by meeting duration until no conflicts.
    pub fn suggest_alternative(&self, employee: &str, mut start_time: u64, duration: u64) -> Result<Vec<u64>, Box<dyn Error>> {
        let mut suggestions = Vec::new();
        // Provide 3 suggestions by checking increments of duration.
        for _ in 0..3 {
            start_time += duration;
            if !self.has_conflict(employee, start_time, duration) {
                suggestions.push(start_time);
            }
        }
        if suggestions.is_empty() {
            return Err(Box::new(SchedulerError("No alternative suggestions found".to_string())));
        }
        Ok(suggestions)
    }

    // For recurring meetings, we generate 12 occurrences (one per month) based on the initial meeting start_time.
    // We assume each month equals 1000 time units for simulation purposes.
    pub fn get_recurrences(&self, meeting: &Meeting) -> Result<Vec<u64>, Box<dyn Error>> {
        let mut occurrences = Vec::new();
        if meeting.recurrence.is_none() {
            return Err(Box::new(SchedulerError("Meeting is not recurring".to_string())));
        }
        // Generate recurrences for next 12 months
        for i in 0..12 {
            let occ = meeting.start_time + i * 1000;
            // Check rule and exception: We simulate by using get_month_of_occurrence.
            let month = self.get_month_of_occurrence(occ);
            if meeting.recurrence.as_ref().unwrap().exceptions.contains(&month) {
                continue;
            }
            // We ignore detailed rule parsing and assume rule string is for display.
            occurrences.push(occ);
        }
        Ok(occurrences)
    }

    // Simulate getting month from timestamp. Each month is 1000 time units.
    // Month = ((timestamp / 1000) % 12) + 1, so timestamps 0-999 -> month 1, etc.
    pub fn get_month_of_occurrence(&self, timestamp: u64) -> u32 {
        ((timestamp / 1000) % 12 + 1) as u32
    }

    // Query global availability:
    // For the given offices, check if there is any meeting scheduled exactly with the given start_time and duration
    // that involves at least one employee from each office.
    // If yes, return true.
    pub fn query_global_availability(&self, office_names: Vec<&str>, start_time: u64, duration: u64) -> Result<bool, Box<dyn Error>> {
        for meeting in self.meetings.values() {
            if meeting.start_time == start_time && meeting.duration == duration {
                let mut offices_covered = Vec::new();
                // Include organizer office if exists.
                if let Some(emp) = self.employees.get(&meeting.organizer) {
                    offices_covered.push(emp.office.clone());
                }
                for participant in meeting.participants.iter() {
                    if let Some(emp) = self.employees.get(participant) {
                        if !offices_covered.contains(&emp.office) {
                            offices_covered.push(emp.office.clone());
                        }
                    }
                }
                // Check if every office in office_names is represented.
                let mut all_present = true;
                for &office in office_names.iter() {
                    if !offices_covered.contains(&office.to_string()) {
                        all_present = false;
                        break;
                    }
                }
                if all_present {
                    return Ok(true);
                }
            }
        }
        Ok(false)
    }

    pub fn cancel_meeting(&mut self, meeting_id: u64) -> Result<(), Box<dyn Error>> {
        if self.meetings.remove(&meeting_id).is_some() {
            Ok(())
        } else {
            Err(Box::new(SchedulerError("Meeting id not found".to_string())))
        }
    }

    // Get all meetings for a given employee.
    pub fn get_meetings_for_employee(&self, employee: &str) -> Result<Vec<Meeting>, Box<dyn Error>> {
        let mut result = Vec::new();
        for meeting in self.meetings.values() {
            if meeting.organizer == employee || meeting.participants.contains(&employee.to_string()) {
                result.push(meeting.clone());
            }
        }
        Ok(result)
    }
}