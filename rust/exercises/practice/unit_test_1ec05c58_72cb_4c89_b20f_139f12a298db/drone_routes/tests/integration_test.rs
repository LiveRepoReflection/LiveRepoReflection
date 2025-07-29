use drone_routes::{plan_routes, Drone, DeliveryRequest, Graph};

#[test]
fn test_single_delivery_no_recharge() {
    let graph = Graph {
        nodes: vec![1, 2],
        edges: vec![(1, 2, 10.0), (2, 1, 10.0)],
        charging_stations: vec![],
    };
    let drones = vec![
        Drone {
            id: 1,
            start: 1,
            battery_capacity: 25.0,
            t_max: 50.0,
        }
    ];
    let deliveries = vec![
        DeliveryRequest {
            id: 101,
            origin: 1,
            destination: 2,
            deadline: 20.0,
        }
    ];
    let t_charge = 5.0;
    let plan = plan_routes(&graph, &drones, &deliveries, t_charge).expect("Should find route");
    assert_eq!(plan.drones_plans.len(), 1);
    let drone_plan = plan.drones_plans.iter().find(|dp| dp.drone_id == 1).unwrap();
    // Expected route: start at 1, deliver from 1 to 2, and return to 1.
    assert_eq!(drone_plan.route, vec![1, 2, 1]);
    // Total flight time should be 10.0 (1->2) + 10.0 (2->1) = 20.0.
    assert!((drone_plan.total_delivery_time - 20.0).abs() < 1e-6);
}

#[test]
fn test_delivery_requires_charging() {
    let graph = Graph {
        nodes: vec![1, 2, 3],
        edges: vec![
            (1, 3, 5.0),
            (3, 2, 5.0),
            (2, 1, 10.0),
            (3, 1, 5.0),
        ],
        charging_stations: vec![3],
    };
    let drones = vec![
        Drone {
            id: 1,
            start: 1,
            battery_capacity: 10.0,
            t_max: 30.0,
        }
    ];
    let deliveries = vec![
        DeliveryRequest {
            id: 102,
            origin: 1,
            destination: 2,
            deadline: 25.0,
        }
    ];
    let t_charge = 3.0;
    let plan = plan_routes(&graph, &drones, &deliveries, t_charge).expect("Should find route with charging");
    let drone_plan = plan.drones_plans.iter().find(|dp| dp.drone_id == 1).unwrap();
    // Check that the route starts and ends at the warehouse.
    assert_eq!(drone_plan.route.first().unwrap(), &1);
    assert_eq!(drone_plan.route.last().unwrap(), &1);
    // The charging station (node 3) should be on the route.
    assert!(drone_plan.route.contains(&3));
    // Delivery destination (node 2) must also be part of the route.
    assert!(drone_plan.route.contains(&2));
    // Ensure total delivery time respects the drone's maximum timeframe.
    assert!(drone_plan.total_delivery_time <= 30.0);
}

#[test]
fn test_multiple_deliveries_multiple_drones() {
    let graph = Graph {
        nodes: vec![1, 2, 3, 4, 5],
        edges: vec![
            (1, 2, 5.0),
            (2, 3, 5.0),
            (3, 4, 5.0),
            (4, 5, 5.0),
            (5, 1, 5.0),
            (1, 3, 8.0),
            (3, 5, 8.0),
        ],
        charging_stations: vec![3],
    };
    let drones = vec![
        Drone {
            id: 1,
            start: 1,
            battery_capacity: 15.0,
            t_max: 40.0,
        },
        Drone {
            id: 2,
            start: 5,
            battery_capacity: 20.0,
            t_max: 50.0,
        },
    ];
    let deliveries = vec![
        DeliveryRequest {
            id: 201,
            origin: 1,
            destination: 4,
            deadline: 30.0,
        },
        DeliveryRequest {
            id: 202,
            origin: 5,
            destination: 2,
            deadline: 35.0,
        },
    ];
    let t_charge = 4.0;
    let plan = plan_routes(&graph, &drones, &deliveries, t_charge).expect("Plan should be computed");
    // Expect both drones to have their own plans.
    assert_eq!(plan.drones_plans.len(), 2);
    for drone in &drones {
        let dp = plan.drones_plans.iter().find(|dp| dp.drone_id == drone.id).expect("Drone plan must exist");
        // Route should start and end at the drone's warehouse.
        assert_eq!(dp.route.first().unwrap(), &drone.start);
        assert_eq!(dp.route.last().unwrap(), &drone.start);
        // Total delivery time must be within the global timeframe.
        if drone.id == 1 {
            assert!(dp.total_delivery_time <= 40.0);
        } else if drone.id == 2 {
            assert!(dp.total_delivery_time <= 50.0);
        }
    }
}

#[test]
fn test_unreachable_delivery() {
    let graph = Graph {
        nodes: vec![1, 2, 3],
        edges: vec![
            (1, 2, 5.0),
            (2, 1, 5.0),
        ],
        charging_stations: vec![],
    };
    let drones = vec![
        Drone {
            id: 1,
            start: 1,
            battery_capacity: 15.0,
            t_max: 30.0,
        }
    ];
    let deliveries = vec![
        DeliveryRequest {
            id: 301,
            origin: 1,
            destination: 3,
            deadline: 20.0,
        }
    ];
    let t_charge = 2.0;
    let result = plan_routes(&graph, &drones, &deliveries, t_charge);
    assert!(result.is_err());
}