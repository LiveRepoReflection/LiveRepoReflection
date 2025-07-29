use data_stream::{AggregationNode, AggregatedData, CentralServer, GlobalAggregates};

#[test]
fn test_aggregation_node_sequential() {
    let mut node = AggregationNode::new();
    let data = vec![(1_u64, 10.0), (2, 20.0), (3, 30.0), (4, 40.0)];
    let aggregated = node.process_data(data).expect("Aggregation failed");
    assert_eq!(aggregated.timestamp_start, 1);
    assert_eq!(aggregated.timestamp_end, 4);
    assert_eq!(aggregated.min, 10.0);
    assert_eq!(aggregated.max, 40.0);
    assert_eq!(aggregated.sum, 100.0);
    assert_eq!(aggregated.count, 4);
}

#[test]
fn test_central_server_single_node() {
    let mut server = CentralServer::new(60, 10);
    let data1 = AggregatedData {
        timestamp_start: 0,
        timestamp_end: 30,
        min: 5.0,
        max: 25.0,
        sum: 150.0,
        count: 10,
        sequence: 1,
    };
    let data2 = AggregatedData {
        timestamp_start: 31,
        timestamp_end: 60,
        min: 4.0,
        max: 30.0,
        sum: 160.0,
        count: 10,
        sequence: 2,
    };
    server.add_aggregated_data(data1);
    server.add_aggregated_data(data2);
    let aggregates = server.get_current_aggregates(60).expect("No aggregates computed");
    assert_eq!(aggregates.min, 4.0);
    assert_eq!(aggregates.max, 30.0);
    let expected_average = (150.0 + 160.0) / 20.0;
    assert!((aggregates.average - expected_average).abs() < 1e-6);
    assert!(aggregates.std_deviation >= 0.0);
}

#[test]
fn test_central_server_multiple_nodes() {
    let mut server = CentralServer::new(120, 30);
    let node1_data = AggregatedData {
        timestamp_start: 10,
        timestamp_end: 70,
        min: 1.0,
        max: 50.0,
        sum: 210.0,
        count: 7,
        sequence: 5,
    };
    let node2_data = AggregatedData {
        timestamp_start: 40,
        timestamp_end: 100,
        min: 2.0,
        max: 60.0,
        sum: 280.0,
        count: 8,
        sequence: 3,
    };
    server.add_aggregated_data(node1_data);
    server.add_aggregated_data(node2_data);
    let aggregates = server.get_current_aggregates(100).expect("No aggregates computed");
    assert_eq!(aggregates.min, 1.0);
    assert_eq!(aggregates.max, 60.0);
    let expected_average = (210.0 + 280.0) / (7 + 8) as f64;
    assert!((aggregates.average - expected_average).abs() < 1e-6);
}

#[test]
fn test_out_of_order_aggregated_data() {
    let mut server = CentralServer::new(60, 10);
    let data1 = AggregatedData {
        timestamp_start: 0,
        timestamp_end: 30,
        min: 10.0,
        max: 50.0,
        sum: 200.0,
        count: 5,
        sequence: 2,
    };
    let data2 = AggregatedData {
        timestamp_start: 31,
        timestamp_end: 60,
        min: 8.0,
        max: 55.0,
        sum: 215.0,
        count: 5,
        sequence: 1,
    };
    server.add_aggregated_data(data1);
    server.add_aggregated_data(data2);
    let aggregates = server.get_current_aggregates(60).expect("No aggregates computed");
    assert_eq!(aggregates.min, 8.0);
    assert_eq!(aggregates.max, 55.0);
    let expected_average = (200.0 + 215.0) / 10.0;
    assert!((aggregates.average - expected_average).abs() < 1e-6);
}

#[test]
fn test_data_loss_detection() {
    let mut server = CentralServer::new(60, 10);
    let data1 = AggregatedData {
        timestamp_start: 0,
        timestamp_end: 30,
        min: 5.0,
        max: 45.0,
        sum: 150.0,
        count: 6,
        sequence: 1,
    };
    let data3 = AggregatedData {
        timestamp_start: 31,
        timestamp_end: 60,
        min: 7.0,
        max: 50.0,
        sum: 180.0,
        count: 6,
        sequence: 3,
    };
    server.add_aggregated_data(data1);
    server.add_aggregated_data(data3);
    let aggregates = server.get_current_aggregates(60).expect("No aggregates computed");
    assert_eq!(aggregates.min, 5.0);
    assert_eq!(aggregates.max, 50.0);
    let total_sum = 150.0 + 180.0;
    let total_count = 6 + 6;
    let expected_avg = total_sum / total_count as f64;
    assert!((aggregates.average - expected_avg).abs() < 1e-6);
}

#[test]
fn test_real_time_aggregation() {
    let mut server = CentralServer::new(30, 5);
    let data_points = vec![
        AggregatedData {
            timestamp_start: 0,
            timestamp_end: 10,
            min: 2.0,
            max: 20.0,
            sum: 50.0,
            count: 4,
            sequence: 1,
        },
        AggregatedData {
            timestamp_start: 11,
            timestamp_end: 20,
            min: 3.0,
            max: 25.0,
            sum: 60.0,
            count: 4,
            sequence: 2,
        },
        AggregatedData {
            timestamp_start: 21,
            timestamp_end: 30,
            min: 1.0,
            max: 30.0,
            sum: 70.0,
            count: 4,
            sequence: 3,
        },
    ];
    for data in data_points {
        server.add_aggregated_data(data);
    }
    let aggregates = server.get_current_aggregates(30).expect("No aggregates computed");
    assert_eq!(aggregates.min, 1.0);
    assert_eq!(aggregates.max, 30.0);
    let total_sum = 50.0 + 60.0 + 70.0;
    let total_count = 4 + 4 + 4;
    let expected_avg = total_sum / total_count as f64;
    assert!((aggregates.average - expected_avg).abs() < 1e-6);
    assert!(aggregates.std_deviation >= 0.0);
}