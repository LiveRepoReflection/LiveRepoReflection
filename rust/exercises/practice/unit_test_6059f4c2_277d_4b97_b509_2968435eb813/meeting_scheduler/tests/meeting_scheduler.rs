use std::collections::HashMap;
use std::error::Error;

// Assuming the meeting_scheduler crate exposes the following structures and functions.
use meeting_scheduler::{
    CalendarSystem, Employee, Meeting, MeetingRequest, RecurrencePattern,
};

#[test]
fn test_single_office_meeting() -> Result<(), Box<dyn Error>> {
    let mut system = CalendarSystem::new();
    system.add_office("NYC", 0); // Timezone offset 0 for simplicity
    system.add_employee("alice", "NYC");
    system.add_employee("bob", "NYC");
    
    let request = MeetingRequest {
        title: "Project Kickoff".to_string(),
        organizer: "alice".to_string(),
        participants: vec!["bob".to_string()],
        start_time: 1_000, // Representing a Unix timestamp (for example)
        duration: 60,      // Duration in minutes
        recurrence: None,
    };
    
    let meeting = system.schedule_meeting(request)?;
    assert_eq!(meeting.title, "Project Kickoff");
    assert_eq!(meeting.organizer, "alice");
    Ok(())
}

#[test]
fn test_conflict_resolution() -> Result<(), Box<dyn Error>> {
    let mut system = CalendarSystem::new();
    system.add_office("NYC", 0);
    system.add_employee("alice", "NYC");
    system.add_employee("bob", "NYC");
    
    // Schedule first meeting
    let request1 = MeetingRequest {
        title: "Team Meeting".to_string(),
        organizer: "alice".to_string(),
        participants: vec!["bob".to_string()],
        start_time: 2_000,
        duration: 60,
        recurrence: None,
    };
    let _meeting1 = system.schedule_meeting(request1)?;
    
    // Attempt to schedule a conflicting meeting (overlapping with the first)
    let request2 = MeetingRequest {
        title: "Overlap Meeting".to_string(),
        organizer: "bob".to_string(),
        participants: vec!["alice".to_string()],
        start_time: 2_050, // 50 minutes into the first meeting
        duration: 60,
        recurrence: None,
    };
    let result = system.schedule_meeting(request2);
    assert!(result.is_err(), "Overlapping meeting should result in an error");
    
    // Test alternative suggestion functionality
    let suggestions = system.suggest_alternative("alice", 2_050, 60)?;
    assert!(!suggestions.is_empty(), "System should provide alternative meeting times");
    Ok(())
}

#[test]
fn test_recurring_meeting() -> Result<(), Box<dyn Error>> {
    let mut system = CalendarSystem::new();
    system.add_office("LA", -8);
    system.add_employee("carol", "LA");
    
    // Define a recurrence pattern for a meeting: third Wednesday every month except December.
    let recurrence = RecurrencePattern {
        rule: "3rd Wednesday".to_string(),
        exceptions: vec![12], // 12 represents December
    };
    
    let request = MeetingRequest {
        title: "Monthly Sync".to_string(),
        organizer: "carol".to_string(),
        participants: vec!["carol".to_string()],
        start_time: 3_000,
        duration: 90,
        recurrence: Some(recurrence),
    };
    let meeting = system.schedule_meeting(request)?;
    let occurrences = system.get_recurrences(&meeting)?;
    assert!(!occurrences.is_empty(), "There should be generated recurrence occurrences");
    
    // Verify that none of the occurrences fall in December.
    for occ in &occurrences {
        let month = system.get_month_of_occurrence(*occ);
        assert!(month != 12, "No occurrence should be scheduled in December");
    }
    Ok(())
}

#[test]
fn test_distributed_query_across_offices() -> Result<(), Box<dyn Error>> {
    let mut system = CalendarSystem::new();
    
    // Add multiple offices with different timezones.
    system.add_office("NYC", 0);
    system.add_office("London", 5);
    system.add_office("Tokyo", 9);
    
    system.add_employee("alice", "NYC");
    system.add_employee("david", "London");
    system.add_employee("emma", "Tokyo");
    
    // Schedule a global meeting involving employees from three offices.
    let request = MeetingRequest {
        title: "Global Strategy".to_string(),
        organizer: "alice".to_string(),
        participants: vec!["david".to_string(), "emma".to_string()],
        start_time: 4_000,
        duration: 120,
        recurrence: None,
    };
    let _meeting = system.schedule_meeting(request)?;
    
    // Query global availability for a common slot across these offices.
    let availability = system.query_global_availability(vec!["NYC", "London", "Tokyo"], 4_000, 120)?;
    assert!(availability, "Global availability should be consistent across offices");
    Ok(())
}

#[test]
fn test_meeting_cancellation() -> Result<(), Box<dyn Error>> {
    let mut system = CalendarSystem::new();
    system.add_office("NYC", 0);
    system.add_employee("alice", "NYC");
    system.add_employee("bob", "NYC");
    
    let request = MeetingRequest {
        title: "Cancellation Test".to_string(),
        organizer: "alice".to_string(),
        participants: vec!["bob".to_string()],
        start_time: 5_000,
        duration: 45,
        recurrence: None,
    };
    
    let meeting = system.schedule_meeting(request)?;
    let meeting_id = meeting.id;
    
    system.cancel_meeting(meeting_id)?;
    
    let meetings = system.get_meetings_for_employee("alice")?;
    for m in meetings {
        assert_ne!(m.id, meeting_id, "Canceled meeting should no longer appear in Alice's schedule");
    }
    Ok(())
}