use std::collections::{HashMap, HashSet};
use std::cell::RefCell;
use std::rc::Rc;
use social_recommend::recommendations;

#[test]
fn test_basic_recommendations() {
    let user_id = 1;
    let local_graph: HashMap<u64, HashSet<u64>> = HashMap::new();
    let mut content_preferences: HashMap<String, f64> = HashMap::new();
    content_preferences.insert("Rust".to_string(), 0.9);
    content_preferences.insert("AI".to_string(), 0.5);
    let seen_content: HashSet<u64> = [100, 101].iter().cloned().collect();

    let call_count = Rc::new(RefCell::new(0));
    let mock_network_sample = {
        let call_count = call_count.clone();
        move |sample_size: usize| -> Vec<(u64, HashMap<String, f64>, HashSet<u64>)> {
            *call_count.borrow_mut() += 1;
            let mut results = Vec::new();
            for i in 0..sample_size {
                let user = 1000 + i as u64;
                let mut prefs = HashMap::new();
                if i % 2 == 0 {
                    prefs.insert("Rust".to_string(), 0.8);
                    prefs.insert("Photography".to_string(), 0.3);
                } else {
                    prefs.insert("AI".to_string(), 0.6);
                    prefs.insert("Travel".to_string(), 0.4);
                }
                let seen: HashSet<u64> = vec![2000 + i as u64].into_iter().collect();
                results.push((user, prefs, seen));
            }
            results
        }
    };

    let num_recommendations = 5;
    let max_network_samples = 3;
    let recs = recommendations(
        user_id,
        &local_graph,
        &content_preferences,
        &seen_content,
        &mock_network_sample,
        num_recommendations,
        max_network_samples,
    );
    // Ensure that the number of recommendations does not exceed the requested count.
    assert!(recs.len() <= num_recommendations);
    // Verify that none of the recommended content IDs have been seen.
    for rec in recs.iter() {
        assert!(!seen_content.contains(rec));
    }
    // Validate that the network sample function was called at least once and not more than max_network_samples.
    let calls = *call_count.borrow();
    assert!(calls > 0 && calls <= max_network_samples);
}

#[test]
fn test_cold_start() {
    // User with no local content preferences or social graph.
    let user_id = 2;
    let local_graph: HashMap<u64, HashSet<u64>> = HashMap::new();
    let content_preferences: HashMap<String, f64> = HashMap::new();
    let seen_content: HashSet<u64> = HashSet::new();

    let call_count = Rc::new(RefCell::new(0));
    let mock_network_sample = {
        let call_count = call_count.clone();
        move |sample_size: usize| -> Vec<(u64, HashMap<String, f64>, HashSet<u64>)> {
            *call_count.borrow_mut() += 1;
            let mut results = Vec::new();
            for i in 0..sample_size {
                let user = 2000 + i as u64;
                let mut prefs = HashMap::new();
                prefs.insert("General".to_string(), 0.5);
                let seen: HashSet<u64> = vec![3000 + i as u64].into_iter().collect();
                results.push((user, prefs, seen));
            }
            results
        }
    };

    let num_recommendations = 3;
    let max_network_samples = 2;
    let recs = recommendations(
        user_id,
        &local_graph,
        &content_preferences,
        &seen_content,
        &mock_network_sample,
        num_recommendations,
        max_network_samples,
    );
    // For cold start, recommendations might be fewer than requested.
    assert!(recs.len() <= num_recommendations);
    // Ensure that all recommendations are unique.
    let unique: HashSet<u64> = recs.iter().cloned().collect();
    assert_eq!(unique.len(), recs.len());
}

#[test]
fn test_insufficient_content() {
    // Simulate a scenario where not enough new content is discovered.
    let user_id = 3;
    let local_graph: HashMap<u64, HashSet<u64>> = HashMap::new();
    let mut content_preferences: HashMap<String, f64> = HashMap::new();
    content_preferences.insert("Music".to_string(), 0.7);
    let seen_content: HashSet<u64> = [4001, 4002, 4003].iter().cloned().collect();

    let call_count = Rc::new(RefCell::new(0));
    // This mock always returns an empty vector, simulating no new content.
    let mock_network_sample = {
        let call_count = call_count.clone();
        move |_sample_size: usize| -> Vec<(u64, HashMap<String, f64>, HashSet<u64>)> {
            *call_count.borrow_mut() += 1;
            Vec::new()
        }
    };

    let num_recommendations = 10;
    let max_network_samples = 3;
    let recs = recommendations(
        user_id,
        &local_graph,
        &content_preferences,
        &seen_content,
        &mock_network_sample,
        num_recommendations,
        max_network_samples,
    );
    // When there is insufficient new content, recommendations may be fewer than requested.
    assert!(recs.len() <= num_recommendations);
    // Ensure that the network sample function was called the maximum allowed number of times.
    let calls = *call_count.borrow();
    assert_eq!(calls, max_network_samples);
}