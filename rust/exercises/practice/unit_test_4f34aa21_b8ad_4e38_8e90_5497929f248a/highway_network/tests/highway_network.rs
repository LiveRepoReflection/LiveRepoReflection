use highway_network::*;

#[test]
fn test_already_connected() {
    let input = "4 3 0
1 2 5
2 3 10
3 4 7
2
1 3 15
2 4 20";
    let result = solve(input);
    assert_eq!(result, 22);
}

#[test]
fn test_needed_highway() {
    let input = "4 2 1
1 2 10
3 4 5
1
2 3 20";
    let result = solve(input);
    assert_eq!(result, 35);
}

#[test]
fn test_multiple_options() {
    let input = "5 2 2
1 2 10
4 5 15
3
2 3 5
3 4 10
2 5 30";
    let result = solve(input);
    assert_eq!(result, 40);
}

#[test]
fn test_partial_connectivity_and_redundant_highways() {
    let input = "4 4 1
1 2 10
1 2 8
2 3 12
3 4 7
1
1 4 5";
    let result = solve(input);
    assert_eq!(result, 20);
}

#[test]
fn test_impossible_connection() {
    let input = "3 0 0
0";
    let result = solve(input);
    assert_eq!(result, -1);
}

#[test]
fn test_large_input() {
    let input = "6 3 2
1 2 3
2 3 4
4 5 2
3
3 4 1
3 6 10
5 6 1";
    let result = solve(input);
    assert_eq!(result, 11);
}