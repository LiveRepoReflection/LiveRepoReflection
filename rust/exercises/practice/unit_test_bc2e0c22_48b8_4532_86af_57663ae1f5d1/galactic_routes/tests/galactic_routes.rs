use galactic_routes::min_intergalactic_travel_time;

#[test]
fn test_single_wormhole_immediate_departure() {
    let wormholes = vec![(0, 1, 10, vec![(0, 20), (30, 40)])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, 0),
        Some(10)
    );
}

#[test]
fn test_single_wormhole_delayed_departure() {
    let wormholes = vec![(0, 1, 10, vec![(0, 20), (30, 40)])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, 5),
        Some(15)
    );
}

#[test]
fn test_single_wormhole_between_windows() {
    let wormholes = vec![(0, 1, 10, vec![(0, 20), (30, 40)])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, 25),
        Some(40)
    );
}

#[test]
fn test_unreachable_destination() {
    let wormholes = vec![(0, 1, 10, vec![(0, 20)])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, 21),
        None
    );
}

#[test]
fn test_multiple_paths() {
    let wormholes = vec![
        (0, 1, 5, vec![(0, 100)]),
        (1, 2, 3, vec![(0, 100)]),
        (0, 2, 15, vec![(0, 100)]),
    ];
    assert_eq!(
        min_intergalactic_travel_time(3, wormholes, 0, 2, 0),
        Some(8)
    );
}

#[test]
fn test_overlapping_windows() {
    let wormholes = vec![(0, 1, 5, vec![(0, 10), (5, 15)])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, 3),
        Some(8)
    );
}

#[test]
fn test_complex_network() {
    let wormholes = vec![
        (0, 1, 5, vec![(0, 10), (20, 30)]),
        (1, 2, 3, vec![(5, 15), (25, 35)]),
        (0, 2, 12, vec![(0, 100)]),
    ];
    assert_eq!(
        min_intergalactic_travel_time(3, wormholes, 0, 2, 0),
        Some(8)
    );
}

#[test]
fn test_large_times_no_overflow() {
    let wormholes = vec![
        (0, 1, 1, vec![(u64::MAX - 10, u64::MAX)]),
    ];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, u64::MAX - 5),
        Some(u64::MAX - 4)
    );
}

#[test]
fn test_overflow_protection() {
    let wormholes = vec![
        (0, 1, 1, vec![(u64::MAX - 1, u64::MAX)]),
    ];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, u64::MAX - 1),
        None
    );
}

#[test]
fn test_empty_wormhole_schedule() {
    let wormholes = vec![(0, 1, 5, vec![])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 1, 0),
        None
    );
}

#[test]
fn test_same_start_and_destination() {
    let wormholes = vec![(0, 1, 5, vec![(0, 100)])];
    assert_eq!(
        min_intergalactic_travel_time(2, wormholes, 0, 0, 0),
        Some(0)
    );
}