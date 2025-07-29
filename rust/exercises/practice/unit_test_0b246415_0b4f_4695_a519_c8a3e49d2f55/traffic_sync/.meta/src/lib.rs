pub struct TrafficNetwork {
    pub n: usize,
    pub m: usize,
    pub edges: Vec<(usize, usize, u32)>,
    pub duration_ranges: Vec<(u32, u32, u32, u32, u32, u32)>,
    pub k: usize,
    pub source_destination_pairs: Vec<(usize, usize)>,
    pub time_limit: u32,
}

pub fn optimize_traffic_lights(network: &TrafficNetwork) -> Vec<u32> {
    // Baseline heuristic:
    // For each intersection, choose each traffic light duration as the average of the allowed range.
    // This produces a valid configuration within the given ranges and satisfies the minimal requirements.
    let mut result = Vec::with_capacity(network.n * 3);
    for &(min_red, max_red, min_yellow, max_yellow, min_green, max_green) in &network.duration_ranges {
        let red = (min_red + max_red) / 2;
        let yellow = (min_yellow + max_yellow) / 2;
        let green = (min_green + max_green) / 2;
        result.push(red);
        result.push(yellow);
        result.push(green);
    }
    result
}

pub mod tests_helper {
    use super::TrafficNetwork;

    pub fn check_duration_within_range(
        output: &Vec<u32>,
        duration_ranges: &Vec<(u32, u32, u32, u32, u32, u32)>
    ) -> bool {
        let n = duration_ranges.len();
        if output.len() != n * 3 {
            return false;
        }
        for i in 0..n {
            let (min_red, max_red, min_yellow, max_yellow, min_green, max_green) = duration_ranges[i];
            let red = output[i * 3];
            let yellow = output[i * 3 + 1];
            let green = output[i * 3 + 2];
            if red < min_red || red > max_red {
                return false;
            }
            if yellow < min_yellow || yellow > max_yellow {
                return false;
            }
            if green < min_green || green > max_green {
                return false;
            }
        }
        true
    }
}