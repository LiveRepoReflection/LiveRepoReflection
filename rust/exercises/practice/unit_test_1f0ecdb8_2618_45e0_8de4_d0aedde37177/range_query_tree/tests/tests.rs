use std::panic;

use range_query_tree::RangeQueryTree;

#[test]
fn test_initial_tree() {
    // Create initial tree with a simple array.
    let initial = vec![1, 2, 3, 4, 5];
    let tree = RangeQueryTree::new(initial.clone());

    // Test range_sum for the full array.
    let sum_full = tree.range_sum(0, 0, 4).expect("Valid version");
    assert_eq!(sum_full, 15);

    // Test a subrange query: indices 1 to 3 -> 2 + 3 + 4 = 9.
    let sum_sub = tree.range_sum(0, 1, 3).expect("Valid version");
    assert_eq!(sum_sub, 9);

    // Test range_min for the full array.
    let min_full = tree.range_min(0, 0, 4).expect("Valid version");
    assert_eq!(min_full, 1);

    // Test range_min for a subrange: indices 2 to 4 -> min(3,4,5) = 3.
    let min_sub = tree.range_min(0, 2, 4).expect("Valid version");
    assert_eq!(min_sub, 3);

    // Test query_version returns the full array.
    let version_array = tree.query_version(0).expect("Valid version");
    assert_eq!(version_array, initial);
}

#[test]
fn test_version_update() {
    let initial = vec![1, 2, 3, 4, 5];
    let mut tree = RangeQueryTree::new(initial);

    // Update version 0: change index 2 to 10. This should create version 1.
    let version1 = tree.update(0, 2, 10);
    // Check that version 0 remains unchanged.
    let original = tree.query_version(0).expect("Valid version");
    assert_eq!(original, vec![1, 2, 3, 4, 5]);

    // Check that version 1 has the updated value.
    let v1_array = tree.query_version(version1).expect("Valid version");
    assert_eq!(v1_array, vec![1, 2, 10, 4, 5]);

    // Test range_sum on version 1 for subrange [2, 4].
    let sum_v1 = tree.range_sum(version1, 2, 4).expect("Valid version");
    // Expected: 10 + 4 + 5 = 19.
    assert_eq!(sum_v1, 19);

    // Test range_min on version 1 for subrange [0, 2].
    let min_v1 = tree.range_min(version1, 0, 2).expect("Valid version");
    // Expected: min(1,2,10) = 1.
    assert_eq!(min_v1, 1);

    // Update version 1: change index 0 to 0. This creates version 2.
    let version2 = tree.update(version1, 0, 0);
    let v2_array = tree.query_version(version2).expect("Valid version");
    assert_eq!(v2_array, vec![0, 2, 10, 4, 5]);

    // Range queries on version 2.
    let sum_v2 = tree.range_sum(version2, 0, 2).expect("Valid version");
    // Expected: 0 + 2 + 10 = 12.
    assert_eq!(sum_v2, 12);

    let min_v2 = tree.range_min(version2, 0, 2).expect("Valid version");
    // Expected: min(0,2,10) = 0.
    assert_eq!(min_v2, 0);
}

#[test]
fn test_multiple_updates_and_queries() {
    let initial = vec![5, 4, 3, 2, 1];
    let mut tree = RangeQueryTree::new(initial);

    // Perform a series of updates creating multiple versions.
    // Version 1: update index 4 to 6 => [5,4,3,2,6]
    let version1 = tree.update(0, 4, 6);
    // Version 2: update index 0 to 7 => [7,4,3,2,6]
    let version2 = tree.update(version1, 0, 7);
    // Version 3: update index 2 to 0 => [7,4,0,2,6]
    let version3 = tree.update(version2, 2, 0);

    // Test range_sum on version 3 for subrange [1,3]: 4+0+2 = 6.
    let sum_v3 = tree.range_sum(version3, 1, 3).expect("Valid version");
    assert_eq!(sum_v3, 6);

    // Test range_min on version 3 for the full range: min(7,4,0,2,6) = 0.
    let min_v3 = tree.range_min(version3, 0, 4).expect("Valid version");
    assert_eq!(min_v3, 0);

    // Verify earlier versions remain intact.
    let v1_array = tree.query_version(version1).expect("Valid version");
    assert_eq!(v1_array, vec![5, 4, 3, 2, 6]);

    let v2_array = tree.query_version(version2).expect("Valid version");
    assert_eq!(v2_array, vec![7, 4, 3, 2, 6]);
}

#[test]
fn test_invalid_version_error_handling() {
    let initial = vec![10, 20, 30];
    let mut tree = RangeQueryTree::new(initial);

    // Update once to create version 1.
    let _version1 = tree.update(0, 1, 25);

    // Now use an invalid version number.
    let invalid_version = 100;
    let sum_result = tree.range_sum(invalid_version, 0, 2);
    assert!(sum_result.is_none(), "Expected None for invalid version in range_sum");

    let min_result = tree.range_min(invalid_version, 0, 2);
    assert!(min_result.is_none(), "Expected None for invalid version in range_min");

    let query_result = tree.query_version(invalid_version);
    assert!(query_result.is_none(), "Expected None for invalid version in query_version");

    // Optionally, test that a panic does not occur for invalid input if errors are handled gracefully.
    let result = panic::catch_unwind(|| {
        let _ = tree.range_sum(invalid_version, 0, 1);
    });
    assert!(result.is_ok());
}

#[test]
fn test_full_range_query() {
    // Test that querying the full range returns the correct sum and min.
    let initial = vec![-3, 0, 2, -1, 5];
    let tree = RangeQueryTree::new(initial.clone());

    // Full range sum: (-3) + 0 + 2 + (-1) + 5 = 3.
    let full_sum = tree.range_sum(0, 0, 4).expect("Valid version");
    assert_eq!(full_sum, 3);

    // Full range min should be -3.
    let full_min = tree.range_min(0, 0, 4).expect("Valid version");
    assert_eq!(full_min, -3);
}