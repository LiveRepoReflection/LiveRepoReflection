use drone_delivery::simulate;

#[test]
fn test_valid_simulation() {
    let input = r#"
    {
        "grid_size": {"rows": 10, "cols": 10},
        "hubs": [
            {"id": 1, "location": [0, 0], "drones": 2}
        ],
        "customers": [
            {"id": 101, "location": [5, 5], "deadline": 100, "weight": 2},
            {"id": 102, "location": [3, 7], "deadline": 110, "weight": 1}
        ],
        "charging_stations": [
            {"location": [2, 2]},
            {"location": [8, 8]}
        ],
        "obstacles": [
            {"location": [4, 4]},
            {"location": [4, 5]}
        ],
        "drone": {"max_capacity": 3, "max_flight_time": 50, "speed": 1, "charging_rate": 1},
        "traversal_cost": 1
    }
    "#;

    let result = simulate(input);
    assert!(result.is_ok(), "Simulation failed on valid input.");
    let schedules = result.unwrap();
    assert!(!schedules.is_empty(), "No drone schedules returned.");

    for schedule in schedules {
        // Each drone schedule should have at least one action and positive total time.
        assert!(!schedule.actions.is_empty(), "No actions scheduled for drone {}", schedule.drone_id);
        assert!(schedule.total_time > 0, "Total time should be positive for drone {}", schedule.drone_id);
        // For this scenario, all deliveries should meet their deadlines.
        assert!(schedule.all_deadlines_met, "Deadlines not met for drone {}", schedule.drone_id);
    }
}

#[test]
fn test_infeasible_deadline() {
    let input = r#"
    {
        "grid_size": {"rows": 5, "cols": 5},
        "hubs": [
            {"id": 1, "location": [0, 0], "drones": 1}
        ],
        "customers": [
            {"id": 101, "location": [4, 4], "deadline": 5, "weight": 1}
        ],
        "charging_stations": [],
        "obstacles": [],
        "drone": {"max_capacity": 2, "max_flight_time": 10, "speed": 1, "charging_rate": 1},
        "traversal_cost": 1
    }
    "#;

    let result = simulate(input);
    assert!(result.is_ok(), "Simulation failed on input with an infeasible deadline.");
    let schedules = result.unwrap();

    // At least one drone schedule should indicate a deadline violation.
    let mut violation_found = false;
    for schedule in schedules {
        if !schedule.all_deadlines_met {
            violation_found = true;
            break;
        }
    }
    assert!(violation_found, "Expected at least one deadline violation.");
}

#[test]
fn test_no_customers() {
    let input = r#"
    {
        "grid_size": {"rows": 10, "cols": 10},
        "hubs": [
            {"id": 1, "location": [0, 0], "drones": 2}
        ],
        "customers": [],
        "charging_stations": [
            {"location": [5, 5]}
        ],
        "obstacles": [],
        "drone": {"max_capacity": 3, "max_flight_time": 50, "speed": 1, "charging_rate": 1},
        "traversal_cost": 1
    }
    "#;

    let result = simulate(input);
    assert!(result.is_ok(), "Simulation failed on input with no customers.");
    let schedules = result.unwrap();

    // When no customers exist the drones should not perform any actions and total time should be zero.
    for schedule in schedules {
        assert!(schedule.actions.is_empty(), "Expected no actions for idle drone {}", schedule.drone_id);
        assert_eq!(schedule.total_time, 0, "Expected total time of 0 for idle drone {}", schedule.drone_id);
    }
}

#[test]
fn test_multiple_hubs_and_drones() {
    let input = r#"
    {
        "grid_size": {"rows": 20, "cols": 20},
        "hubs": [
            {"id": 1, "location": [0, 0], "drones": 2},
            {"id": 2, "location": [19, 19], "drones": 3}
        ],
        "customers": [
            {"id": 201, "location": [5, 5], "deadline": 80, "weight": 2},
            {"id": 202, "location": [15, 15], "deadline": 90, "weight": 1},
            {"id": 203, "location": [10, 10], "deadline": 100, "weight": 1}
        ],
        "charging_stations": [
            {"location": [10, 0]},
            {"location": [0, 10]},
            {"location": [10, 20]},
            {"location": [20, 10]}
        ],
        "obstacles": [
            {"location": [8, 8]},
            {"location": [9, 9]},
            {"location": [10, 9]}
        ],
        "drone": {"max_capacity": 3, "max_flight_time": 60, "speed": 1, "charging_rate": 1},
        "traversal_cost": 1
    }
    "#;

    let result = simulate(input);
    assert!(result.is_ok(), "Simulation failed on multiple hubs input.");
    let schedules = result.unwrap();

    let mut hub1_found = false;
    let mut hub2_found = false;
    for schedule in schedules {
        assert!(!schedule.actions.is_empty(), "Expected actions for drone {}", schedule.drone_id);
        if schedule.hub_id == 1 {
            hub1_found = true;
        } else if schedule.hub_id == 2 {
            hub2_found = true;
        }
    }
    assert!(hub1_found, "Expected at least one drone scheduled from hub 1.");
    assert!(hub2_found, "Expected at least one drone scheduled from hub 2.");
}

#[test]
fn test_charging_behavior() {
    let input = r#"
    {
        "grid_size": {"rows": 15, "cols": 15},
        "hubs": [
            {"id": 1, "location": [0, 0], "drones": 1}
        ],
        "customers": [
            {"id": 301, "location": [14, 14], "deadline": 120, "weight": 1}
        ],
        "charging_stations": [
            {"location": [7, 7]}
        ],
        "obstacles": [],
        "drone": {"max_capacity": 2, "max_flight_time": 30, "speed": 1, "charging_rate": 1},
        "traversal_cost": 1
    }
    "#;

    let result = simulate(input);
    assert!(result.is_ok(), "Simulation failed on charging behavior test.");
    let schedules = result.unwrap();
    assert!(!schedules.is_empty(), "No drone schedules returned.");

    for schedule in schedules {
        let mut charging_found = false;
        for action in &schedule.actions {
            if action.action_type == "charge" {
                charging_found = true;
                break;
            }
        }
        assert!(charging_found, "Expected at least one charging action in drone {}", schedule.drone_id);
    }
}