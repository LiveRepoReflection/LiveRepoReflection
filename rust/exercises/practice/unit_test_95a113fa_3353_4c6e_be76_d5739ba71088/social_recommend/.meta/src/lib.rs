use std::collections::{HashMap, HashSet};
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

pub fn recommendations(
    _user_id: u64,
    _local_graph: &HashMap<u64, HashSet<u64>>,
    content_preferences: &HashMap<String, f64>,
    seen_content: &HashSet<u64>,
    network_sample_fn: &dyn Fn(usize) -> Vec<(u64, HashMap<String, f64>, HashSet<u64>)>,
    num_recommendations: usize,
    max_network_samples: usize,
) -> Vec<u64> {
    // Start with the user's own content preferences.
    let mut aggregated: HashMap<String, f64> = content_preferences.clone();
    // If cold start (no preferences), add a default preference.
    if aggregated.is_empty() {
        aggregated.insert("General".to_string(), 0.5);
    }
    
    // Perform network sampling up to the maximum allowed samples.
    let mut samples_taken = 0;
    while samples_taken < max_network_samples {
        // Determine sample size strategically. Here we choose a fixed sample size.
        let sample_size = 3;
        let samples = network_sample_fn(sample_size);
        // If no samples are returned, still count the call.
        if !samples.is_empty() {
            // Update aggregated preferences with sample data.
            for (_peer_id, peer_prefs, _peer_seen) in samples.iter() {
                for (tag, weight) in peer_prefs.iter() {
                    let entry = aggregated.entry(tag.clone()).or_insert(0.0);
                    // Incorporate the peer's weight with a diminishing factor.
                    *entry += weight / ((samples_taken + 1) as f64);
                }
            }
        }
        samples_taken += 1;
    }
    
    // Generate candidate content IDs based on aggregated tags.
    // For diversity, generate multiple candidates per tag.
    let mut candidates: Vec<(u64, f64)> = Vec::new();
    for (tag, weight) in aggregated.iter() {
        // Generate 3 candidates for each tag.
        for i in 0..3 {
            let mut hasher = DefaultHasher::new();
            tag.hash(&mut hasher);
            i.hash(&mut hasher);
            let candidate_id = hasher.finish();
            candidates.push((candidate_id, *weight));
        }
    }
    
    // Sort candidates by descending weight (score).
    candidates.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    
    // Filter out content that has already been seen and ensure uniqueness.
    let mut recommendations = Vec::new();
    let mut seen_candidates = HashSet::new();
    for (candidate, _score) in candidates {
        if recommendations.len() >= num_recommendations {
            break;
        }
        if seen_content.contains(&candidate) {
            continue;
        }
        if seen_candidates.contains(&candidate) {
            continue;
        }
        recommendations.push(candidate);
        seen_candidates.insert(candidate);
    }
    
    recommendations
}